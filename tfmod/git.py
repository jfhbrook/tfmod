from dataclasses import dataclass
import os
import re
import shlex
import subprocess
from typing import Dict, List, Literal, Optional

from tfmod.constants import GIT_BIN
from tfmod.error import GitError

Direction = Literal["fetch"] | Literal["push"]


def run_git(command: List[str], path: str = os.getcwd()) -> str:
    argv = [GIT_BIN] + command
    proc = subprocess.run([GIT_BIN] + command, cwd=path, capture_output=True)
    print(proc.stderr.decode("unicode_escape"))
    try:
        proc.check_returncode()
    except subprocess.CalledProcessError as exc:
        raise GitError(
            f'"{shlex.join(argv)}" exited unsuccessfully (status: {exc.returncode})'
        )
    else:
        if proc.stderr:
            print(proc.stderr)
    # NOTE: This *may* not technically be safe to do, but here's hoping...
    return proc.stdout.decode("unicode_escape")


def run_git_no_capture(command: List[str], path: str = os.getcwd()) -> None:
    proc = subprocess.run([GIT_BIN] + command, cwd=path, capture_output=False)
    try:
        proc.check_returncode()
    except subprocess.CalledProcessError as exc:
        raise GitError(str(exc))


@dataclass
class GitRemote:
    # NOTE: It may be possible that either of these is optional. But I don't
    # see any documentation for that in git and haven't seen it in practice.
    fetch_url: str
    push_url: str

    def parse(self, direction: Direction = "push"):
        url = self.push_url if direction == "push" else self.fetch_url
        raise NotImplementedError("GitRemote#parse()")


def git_remote(path: str = os.getcwd()) -> Dict[str, GitRemote]:
    out = run_git(["remote", "-v"], path).strip()

    remotes: Dict[str, Dict[str, str]] = dict()
    for line in out.split("\n"):
        name, url, direction = re.split(r"\s+", line)
        direction = direction[1:-1]
        if name not in remotes:
            remotes[name] = dict()
        remotes[name][f"{direction}_url"] = url

    return {name: GitRemote(**kwargs) for name, kwargs in remotes.items()}


def git_current_branch(path: str = os.getcwd()) -> str:
    return run_git(["rev-parse", "--abbrev-ref", "HEAD"], path).strip()


@dataclass
class GitRepo:
    remotes: Dict[str, GitRemote]
    current_branch: str
    path: str

    @classmethod
    def load(cls, path: str = os.getcwd()) -> "GitRepo":
        remotes = git_remote(path)
        current_branch = git_current_branch(path)

        return GitRepo(remotes=remotes, current_branch=current_branch, path=path)

    @classmethod
    def init(cls, path: str = os.getcwd()) -> "GitRepo":
        run_git_no_capture(["init"], path)
        return cls.load(path)

    def dirty(self) -> bool:
        raise NotImplementedError("git_is_dirty()")

    def add(self, what: str) -> None:
        run_git_no_capture(["add", what], self.path)

    def commit(self, message: Optional[str] = None) -> None:
        argv = ["commit"]
        if message:
            argv += ["-m", message]
        run_git_no_capture(argv, self.path)
