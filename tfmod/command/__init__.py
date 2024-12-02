import os
import os.path
from typing import Optional

import flag

from tfmod.command.base import cli, command, CommandArgs, exit, Flag, run
from tfmod.constants import TFMOD_VERSION
from tfmod.error import Error
from tfmod.gh import get_gh_user, GhHosts, load_gh_hosts_optional
from tfmod.io import logger
from tfmod.publish import publish as _publish
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
def version_cmd(_args: CommandArgs) -> None:
    """
    Show the current TfMod version
    """
    version()


@command()
def init(_args: CommandArgs) -> None:
    """
    Initialize a new project
    """

    hosts: Optional[GhHosts] = load_gh_hosts_optional()
    default_namespace: Optional[str] = None

    gh_user: Optional[str] = get_gh_user(hosts)

    if gh_user:
        logger.info(f"Using gh user {gh_user} as the default namespace")
        default_namespace = gh_user

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


@command(flags=dict(
    force=Flag(flag.bool_, "force", False, "Force TfMod to publish, even when dangerous"),
    auto_approve=Flag(flag.bool_, "auto-approve", False, "Automatically approve the publish plan")
))
def publish(args: CommandArgs) -> None:
    """
    Publish the current
    """

    _publish(args)


@command()
def config(_args: CommandArgs) -> None:
    """
    Configure TfMod
    """

    cmd = Terraform("config-command").args(flag.args)

    cmd.run()


@command()
def update(_args: CommandArgs) -> None:
    """
    Install or update TfMod and its dependencies
    """

    # TODO: Better error
    raise Error("This command is implemented in Bash")


@command()
def unwise(_args: CommandArgs) -> None:
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
