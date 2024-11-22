import flag

from tfmod.cli.base import command, Command, parse
from tfmod.config import init_config
from tfmod.terraform import run_terraform


@command()
def init(cmd: Command) -> None:
    """
    initialize a new project
    """

    run_terraform("init-command", flag.args)


@command()
def config(_cmd: Command) -> None:
    """
    configure tfmod
    """

    run_terraform("config-command", flag.args)


def main() -> None:
    parse()
