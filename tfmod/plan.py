from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, cast, List, Literal, Optional, Self, Tuple, Type

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

    _singleton: "Optional[Resource[T]]" = None

    name: str = "<none>"

    def __init__(self: Self) -> None:
        self._cached: Optional[T] = None
        pprint(f"[bold]{self.name}: Refreshing state...[/bold]")

    def may(self: Self) -> Optional[T]:
        if self._cached is not None:
            return self._cached
        maybe = self.get()
        if maybe is not None:
            self.validate(maybe)
            self._cached = maybe
        return maybe

    def must(self: Self) -> T:
        maybe = self.may()
        if not maybe:
            raise ResourceError("Resource can not be resolved")
        return maybe

    def clear(self: Self) -> None:
        self._cached = None

    @abstractmethod
    def get(self: Self) -> Optional[T]:
        """
        Attempt to get the resource. If the resource isn't ready, None must be
        returned.
        """
        raise NotImplementedError("_get")

    def validate(self: Self, resource: T) -> None:
        """
        Validate the resource. This hook is run when a resource first resolved.
        """
        pass


def _singleton[T](cls: Type[Resource[T]]) -> Resource[T]:
    # Pyright doesn't like inferring class properties of generic types.
    # There's probably a way to type this, but we're already pulling serious
    # shenanigans
    singleton = cast(Any, cls)._singleton

    if not singleton:
        singleton = cls()
        cast(Any, cls)._singleton = singleton

    if not singleton:
        raise ResourceError("Resource singletonance not found")

    return singleton


def may[T](cls: Type[Resource[T]]) -> Optional[T]:
    """
    Attempt to get the resource. If the resource isn't ready, None is
    returned. Successful attempts are cached.
    """
    return _singleton(cls).may()


def must[T](cls: Type[Resource[T]]) -> T:
    """
    Get the resource. If the resource isn't ready, raises a
    ResourceError. Successful attempts are cached.
    """
    return _singleton(cls).must()


def clear[T](cls: Type[Resource[T]]) -> None:
    """
    Clear the resource, as though it has never been received.
    """
    _singleton(cls).clear()


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
