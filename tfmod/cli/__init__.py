import flag

from tfmod.cli.base import command, Command, parse
from tfmod.config import init_config
from tfmod.terraform import run_terraform


@command()
def init(cmd: Command) -> None:
    """
    initialize a new project
    """

    run_terraform(cmd.name, flag.args)


@command()
def config(_cmd: Command) -> None:
    """
    configure tfmod
    """
    init_config()


def main() -> None:
    parse()
