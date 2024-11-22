import flag

from tfmod.cli.base import command, Command, parse
from tfmod.terraform import run_terraform


@command()
def init(cmd: Command) -> None:
    """
    initialize a new project
    """

    run_terraform(cmd.name, flag.args)


def main() -> None:
    parse()
