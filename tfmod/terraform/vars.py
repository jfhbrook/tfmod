from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import hcl2
from rich import print as pprint

from tfmod import MODULES_DIR

# Make the type checker happy
hcl: Any = hcl2


def prompt_var(default_: Optional[str]) -> str:
    """
    Prompt for a variable value
    """

    msg = "Enter a value"
    if default_:
        msg += f" ({default_})"
    msg += ":"
    # rich.Prompt doesn't have the right behavior.
    #
    # I'd use a formatter from rich, but it doesn't expose one. This is
    # probably because it goes through great pains to handle terminal width
    # appropriately, something a format method can't do.
    try:
        return input(f"\u001b[1m{msg}\u001b[0m ")
    except KeyboardInterrupt:
        print("")
        raise


@dataclass
class Variable:
    """
    A Terraform variable
    """

    description: Optional[str]
    type: Optional[str]
    default: Optional[Any]


def load_variables(module: Path) -> Dict[str, Variable]:
    """
    Load the variables defined in a module
    """
    with open(module / "variables.tf", "r") as f:
        data: Dict[str, Any] = hcl.load(f)

    rv: Dict[str, Variable] = dict()

    for var in data["variable"]:
        items: List[Tuple[str, Any]] = list(var.items())
        assert len(items) == 1
        name, contents = items[0]

        rv[name] = Variable(
            description=contents.get("description", None),
            type=contents.get("type", None),
            default=contents.get("default", None),
        )

    return rv


def prompt_vars(
    module: str,
    defaults: Optional[Dict[str, str]] = None,
    ignore: Optional[Set[str]] = None,
) -> Dict[str, str]:
    """
    Prompt for variable values in a module.

    This function differs from Terraform's standard behavior in that it
    prompts for variables, even if they have defaults.
    """

    defs = defaults if defaults else dict()
    ign = ignore if ignore else set()

    variables = load_variables(MODULES_DIR / module)

    rv: Dict[str, str] = dict()
    for name, var in variables.items():
        if name in ign:
            continue

        default_: Any = defs[name] if name in defs else var.default
        if type(default_) != str:
            default_ = None

        pprint(f"[bold]var.{name}[/bold]")
        if var.description:
            pprint(f"  [bold]{var.description}[/bold]")
        print("")
        value = prompt_var(default_)
        rv[name] = value if value else default_
        print("")

    return rv
