from typing import List

import flag

from tfmod import TFMOD_VERSION
from tfmod.cli.base import cli, command, Command, exit, run
from tfmod.terraform import run_terraform
from tfmod.vars import prompt_vars


def check_for_updates() -> None:
    """
    Check for updates
    """
    pass


def version() -> None:
    """
    Show the current TfMod version and check for updates
    """

    print(f"TfMod v{TFMOD_VERSION}")
    check_for_updates()


@command(name="version")
def version_cmd(_cmd: Command) -> None:
    """
    Show the current TfMod version
    """
    version()


@command()
def init(_cmd: Command) -> None:
    """
    Initialize a new project
    """

    variables = prompt_vars("init-command")

    args: List[str] = []

    for name, value in variables.items():
        if value is not None:
            args += ["-var", f"{name}={value}"]

    run_terraform("init-command", args + flag.args)


@command()
def config(_cmd: Command) -> None:
    """
    Configure TfMod
    """

    run_terraform("config-command", flag.args)


@cli
def main() -> None:
    """
    The TfMod command line interface
    """

    v = flag.Ptr(False)

    flag.bool_var(v, "version", False, 'An alias for the "version" subcommand.')

    flag.parse()

    if v:
        version()
        exit()

    run()
