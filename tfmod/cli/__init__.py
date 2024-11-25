from typing import NoReturn

import flag

from tfmod import TFMOD_VERSION
from tfmod.cli.base import cli, command, Command, exit, run
from tfmod.terraform import run_terraform


def check_for_updates() -> None:
    """
    Check for updates
    """
    pass


def version() -> None:
    """
    Show TfMod version and check for updates
    """

    print(f"TfMod v{TFMOD_VERSION}")
    check_for_updates()


@command()
def init(_cmd: Command) -> None:
    """
    Initialize a new project
    """

    run_terraform("init-command", flag.args)


@command()
def config(_cmd: Command) -> None:
    """
    Configure TfMod
    """

    run_terraform("config-command", flag.args)


@cli
def main() -> None:
    """
    The command line entry point
    """

    v = flag.Ptr(False)

    flag.bool_var(v, "version", False, "Show TfMod version")
    flag.bool_var(v, "v", False, "Alias for -version")

    flag.parse()

    if v:
        version()
        exit()

    run()
