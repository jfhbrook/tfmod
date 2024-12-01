from dataclasses import dataclass
import os
from pathlib import Path
import shlex
import subprocess
from typing import Dict, List, Optional

from github import Auth, Github
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from tfmod.constants import GH_BIN, GH_CONFIG_DIR
from tfmod.error import GhError
from tfmod.io import logger


@dataclass
class GhUser:
    pass


@dataclass
class GhHost:
    git_protocol: Optional[str]
    users: Dict[str, GhUser]
    user: Optional[str]


GhHosts = Dict[str, GhHost]


def load_gh_hosts(path: Path = GH_CONFIG_DIR / "hosts.yml") -> GhHosts:
    with open(path, "r") as f:
        data = load(f, Loader=Loader)

    # TODO: Check/warn for unexpected keys
    hosts = {
        name: GhHost(
            git_protocol=host.get("git_protocol", None),
            users={name: GhUser() for name, _ in host["users"].items()},
            user=host.get("user", None),
        )
        for name, host in data.items()
    }

    logger.info("Loaded gh hosts")

    return hosts


def load_gh_hosts_optional(
    path: Path = GH_CONFIG_DIR / "hosts.yml",
) -> Optional[GhHosts]:
    try:
        return load_gh_hosts(path)
    except FileNotFoundError:
        logger.debug("gh hosts.yml not found")


def get_gh_user(hosts: Optional[GhHosts]) -> Optional[str]:
    if not hosts:
        return None
    if "github.com" in hosts:
        host = hosts["github.com"]
        if host.user:
            logger.info(f"Found gh user {host.user}")
            return host.user
        else:
            logger.debug("No user defined in gh hosts")
    else:
        logger.debug("github.com not found in gh hosts")


# TODO: This is mostly copy-paste from git.py...
def gh_out(command: List[str], path: str = os.getcwd()) -> str:
    argv = [GH_BIN] + command
    proc = subprocess.run([GH_BIN] + command, cwd=path, capture_output=True)
    print(proc.stderr.decode("unicode_escape"))
    try:
        proc.check_returncode()
    except subprocess.CalledProcessError as exc:
        raise GhError(
            f'"{shlex.join(argv)}" exited unsuccessfully (status: {exc.returncode})'
        )
    else:
        if proc.stderr:
            print(proc.stderr)
    # NOTE: This *may* not technically be safe to do, but here's hoping...
    return proc.stdout.decode("unicode_escape")


# TODO: What happens if I log out?
def gh_auth_token(host: str = "github.com", user: Optional[str] = None) -> Auth.Token:
    argv = ["auth", "token", "-h", host]
    if user is not None:
        argv.append("-u")
        argv.append(user)
    return Auth.Token(gh_out(argv).strip())


def gh_client(host: str = "github.com", user: Optional[str] = None) -> Github:
    auth = gh_auth_token(host, user)
    return Github(auth=auth)
