from dataclasses import dataclass
import os
import re
import subprocess
from typing import Dict, Literal, Optional

from tfmod.constants import GIT_BIN
from tfmod.error import GitError

Direction = Literal["fetch"] | Literal["push"]


@dataclass
class GitRemote:
    # NOTE: It may be possible that either of these is optional. But I don't
    # see any documentation for that in git and haven't seen it in practice.
    fetch_url: str
    push_url: str

    def parse(self, direction: Direction = "push"):
        url = self.push_url if direction == "push" else self.fetch_url
        raise NotImplementedError("GitRemote#parse()")


def git_remote(path: str = os.getcwd()):
    proc = subprocess.run([GIT_BIN, "remote", "-v"], cwd=path, capture_output=True)
    print(proc.stderr)
    try:
        proc.check_returncode()
    except subprocess.CalledProcessError as exc:
        raise GitError(str(exc))
    else:
        if proc.stderr:
            print(proc.stderr)
    out = proc.stdout.decode("unicode_escape")

    remotes: Dict[str, Dict[str, str]] = dict()
    for line in out.split("\n"):
        name, url, direction = re.split(r"\s+", line)
        direction = direction[1:-1]
        if name not in remotes:
            remotes[name] = dict()
        remotes[name][f"{direction}_url"] = url

    return {name: GitRemote(**kwargs) for name, kwargs in remotes.items()}


@dataclass
class GitRepo:
    remotes: Dict[str, str]
    current_branch: str

    @classmethod
    def load(cls) -> "GitRepo":
        raise NotImplementedError("GitRepo.load()")


def git_init() -> None:
    raise NotImplementedError("git_init()")


def git_is_dirty() -> None:
    raise NotImplementedError("git_is_dirty()")


def git_add(path: str) -> None:
    raise NotImplementedError("git_add()")


def git_commit(message: Optional[str] = None) -> None:
    raise NotImplementedError("git_commit()")
