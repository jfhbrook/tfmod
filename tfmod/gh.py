from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from tfmod.constants import GH_CONFIG_DIR


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
    return {
        name: GhHost(
            git_protocol=host.get("git_protocol", None),
            users={name: GhUser() for name, _ in host["users"].items()},
            user=host.get("user", None),
        )
        for name, host in data.items()
    }
