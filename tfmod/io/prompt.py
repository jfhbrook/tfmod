import textwrap
from typing import Optional

from rich import print as pprint

from tfmod.interrupts import interrupt_received
from tfmod.terraform.value import dump_value, load_value, Value


def prompt(
    name: str, message: str = "Enter a value:", description: Optional[str] = None
) -> Optional[str]:
    """
    A general prompt
    """

    pprint(f"[bold]{name}[/bold]")
    if description:
        pprint(f"[bold]{textwrap.indent(description, " ")}[/bold]")
    print("")

    # rich.Prompt doesn't have the right behavior.
    #
    # I'd use a formatter from rich, but it doesn't expose one. This is
    # probably because it goes through great pains to handle terminal width
    # appropriately, something a format method can't do.
    try:
        result = input(f"\u001b[1m{message}\u001b[0m ")
    except (KeyboardInterrupt, EOFError):
        print()
        interrupt_received()
        raise
    print("")
    return result


DEFAULT_CONFIRM_QUESTION = "Do you want to perform these actions?"
DEFAULT_CONFIRM_DESCRIPTION = """TfMod will perform the actions described above.
Only 'yes' will be accepted to approve."""


def prompt_confirm(
    question: str = DEFAULT_CONFIRM_QUESTION, description=DEFAULT_CONFIRM_DESCRIPTION
) -> bool:
    """
    Prompt to confirm y/N
    """

    result = prompt(question, "Enter a value:", description)

    if result in ["y", "Y", "yes", "YES"]:
        return True
    return False


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
        print()
        interrupt_received()
        raise
    else:
        print("")

    if result == "":
        return default

    return load_value(result)
