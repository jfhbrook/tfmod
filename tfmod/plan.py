from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, List, Literal, Optional, Self, Tuple

from rich import print as pprint

from tfmod.error import ApplyInterruptError, ResourceError
from tfmod.io import prompt_confirm

ActionType = Literal["+"] | Literal["~"] | Literal["-"]


@dataclass
class Action:
    type: ActionType
    name: str
    run: Callable[[], Any]


Plan = List[Action]


def _action_types(actions: List[Action]) -> Tuple[int, int, int]:
    create: int = 0
    update: int = 0
    destroy: int = 0
    for action in actions:
        if action.type == "+":
            create += 1
        elif action.type == "~":
            update += 1
        elif action.type == "-":
            destroy += 1
    return create, update, destroy


ACTION_MARKER = {
    "+": "[green]+[/green]",
    "~": "[yellow]~[/yellow]",
    "-": "[red]-[/red]",
}


class Resource[T](ABC):
    """
    A resource.
    """

    def __init__(self: Self) -> None:
        self._cached: Optional[T] = None

    def may(self: Self) -> Optional[T]:
        if self._cached is not None:
            return self._cached
        maybe = self._get()
        if maybe is not None:
            self._cached = maybe
        return maybe

    def must(self: Self) -> T:
        maybe = self.may()
        if not maybe:
            raise ResourceError("Resource can not be resolved")
        return maybe

    @abstractmethod
    def _get(self: Self) -> Optional[T]:
        raise NotImplementedError("_get")

    @abstractmethod
    def _validate(self: Self, obj: T) -> None:
        raise NotImplementedError("_validate")


def no_changes(plan: Plan) -> bool:
    if not plan:
        pprint("[green]No changes.[/green] Your module matches the configuration.")
        return True
    return False


def prompt_apply(actions: List[Action]) -> bool:
    assert not no_changes(actions)

    create, update, destroy = _action_types(actions)
    print(
        "TfMod generated the following execution plan. "
        "Actions are indicated with the following symbols:"
    )

    if create:
        pprint("  [green]+[/green] create")
    if update:
        pprint("  [yellow]~[/yellow] update in-place")
    if destroy:
        pprint("  [red]-[/red] destroy")

    print("")
    print("TfMod will perform the following actions:")
    print("")

    for action in actions:
        pprint(f"  {ACTION_MARKER[action.type]} {action.name}")

    print("")

    print(f"Plan: {create} to add, {update} to change, {destroy} to destroy.")
    print("")
    return prompt_confirm(
        "Do you want to perform these actions?",
        """TfMod will perform the actions described above.
Only 'yes' will be accepted to approve.""",
    )


def apply(plan: Plan) -> None:
    if no_changes(plan):
        return

    if prompt_apply(plan):
        for action in plan:
            action.run()
    else:
        raise ApplyInterruptError("error asking for approval: interrupted")
