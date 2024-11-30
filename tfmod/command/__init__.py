import os
import os.path
from typing import Optional

import flag

from tfmod.command.base import cli, command, Command, exit, run
from tfmod.constants import TFMOD_VERSION
from tfmod.error import Error
from tfmod.gh import GhHosts, load_gh_hosts
from tfmod.io import logger
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

    hosts: Optional[GhHosts] = None
    try:
        hosts = load_gh_hosts()
        logger.info("Loaded gh hosts")
    except FileNotFoundError:
        logger.debug("gh hosts.yml not found")

    default_namespace: Optional[str] = None

    if hosts:
        if "github.com" in hosts:
            host = hosts["github.com"]
            if host.user:
                logger.info(f"Using gh user {host.user} as the default namespace")
                default_namespace = host.user
            else:
                logger.debug("No user defined in gh hosts")
        else:
            logger.debug("github.com not found in gh hosts")

    cmd = (
        Terraform("init")
        .isolated_state()
        .spec()
        .prompt_var("namespace", default=default_namespace)
        .prompt_var("name", default=os.path.basename(os.getcwd()))
        .prompt_var("provider_")
        .prompt_var("version_")
        .prompt_var("description")
        .auto_approve()
    )

    cmd.run()


@command()
def config(_cmd: Command) -> None:
    """
    Configure TfMod
    """

    cmd = Terraform("config-command").args(flag.args)

    cmd.run()


@command()
def update(_cmd: Command) -> None:
    """
    Install or update TfMod and its dependencies
    """

    # TODO: Better error
    raise Error("This command is implemented in Bash")


@command()
def unwise(_cmd: Command) -> None:
    """
    Remove TfMod and its files.
    """

    # TODO: Better error
    raise Error("This command is implemented in Bash")


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
