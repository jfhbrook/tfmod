from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from github import Auth, Github
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from tfmod.constants import GH_CONFIG_DIR
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


def gh_auth_token(host: str = "github.com", user: Optional[str] = None) -> Auth.Token:
    raise NotImplementedError("gh_auth_token()")


def gh_client(host: str = "github.com", user: Optional[str] = None) -> Github:
    auth = gh_auth_token(host, user)
    return Github(auth=auth)
