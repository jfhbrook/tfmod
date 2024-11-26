import os
import os.path
from typing import Optional

import flag

from tfmod.cli.base import cli, command, Command, exit, run
from tfmod.constants import TFMOD_VERSION
from tfmod.module import Module
from tfmod.terraform import Terraform


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

    name: str = os.path.basename(os.getcwd())
    provider: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None

    module: Optional[Module] = Module.load_optional()

    if module:
        name = module.name if module.name else name
        provider = module.provider
        version = module.version
        description = module.description

    cmd = (
        Terraform("init")
        .prompt_var("name", default=name)
        .prompt_var("provider_", default=provider)
        .prompt_var("version_", default=version)
        .prompt_var("description", default=description)
    )

    cmd.run()


@command()
def config(_cmd: Command) -> None:
    """
    Configure TfMod
    """

    cmd = Terraform("config-command").args(flag.args)

    cmd.run()


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
