from typing import Any, Dict, List, Optional

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
    return input(f"\u001b[1m{msg}\u001b[0m ")


def prompt_vars(module: str) -> Dict[str, str]:
    """
    Prompt for variable values in a module.

    This function differs from Terraform's standard behavior in that it
    prompts for variables, even if they have defaults.
    """

    with open(MODULES_DIR / module / "variables.tf", "r") as f:
        variables: Dict[str, List[Any]] = hcl.load(f)

    rv: Dict[str, str] = dict()
    for var in variables["variable"]:
        items = list(var.items())
        assert len(items) == 1

        name, contents = items[0]

        description: Optional[str] = contents.get("description", None)

        default_: Any = contents.get("default", None)
        if type(default_) != str:
            default_ = None

        pprint(f"[bold]var.{name}[/bold]")
        if description:
            pprint(f"  [bold]{description}[/bold]")
        print("")
        value = prompt_var(default_)
        rv[name] = value if value else default_
        print("")

    return rv
