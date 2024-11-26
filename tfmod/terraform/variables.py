from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import hcl2
from rich import print as pprint

from tfmod.interrupts import interrupt_received
from tfmod.terraform.value import dump_value, load_value, Value

# Make the type checker happy
hcl: Any = hcl2


def prompt_var(
    name: str, description: Optional[str] = None, default: Optional[Value] = None
) -> Optional[Value]:
    """
    Prompt for a variable value
    """

    pprint(f"[bold]var.{name}[/bold]")
    if description:
        pprint(f"  [bold]{description}[/bold]")
    print("")

    msg = "Enter a value"

    if default is not None:
        msg += f" ({dump_value(default)})"
    msg += ":"

    # rich.Prompt doesn't have the right behavior.
    #
    # I'd use a formatter from rich, but it doesn't expose one. This is
    # probably because it goes through great pains to handle terminal width
    # appropriately, something a format method can't do.
    try:
        result = input(f"\u001b[1m{msg}\u001b[0m ")
    except (KeyboardInterrupt, EOFError):
        interrupt_received()
        raise
    else:
        print("")

    if result == "":
        return default

    return load_value(result)


@dataclass
class Variable:
    """
    A Terraform variable
    """

    description: Optional[str] = None
    type: Optional[str] = None
    default: Optional[Value] = None


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
