from dataclasses import dataclass
import os
import re
import shlex
import subprocess
from typing import Dict, List, Literal, Optional

from tfmod.constants import GIT_BIN
from tfmod.error import GitError
from tfmod.io import logger

Direction = Literal["fetch"] | Literal["push"]


def git_out(command: List[str], path: str = os.getcwd()) -> str:
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


def git_test(command: List[str], path: str = os.getcwd()) -> bool:
    argv = [GIT_BIN] + command
    proc = subprocess.run([GIT_BIN] + command, cwd=path, capture_output=True)
    logger.trace(f"Running: {shlex.join(argv)}")
    logger.trace(proc.stderr.decode("unicode_escape"))

    return proc.returncode == 0


def git_interactive(command: List[str], path: str = os.getcwd()) -> None:
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
    out = git_out(["remote", "-v"], path).strip()

    remotes: Dict[str, Dict[str, str]] = dict()
    for line in out.split("\n"):
        name, url, direction = re.split(r"\s+", line)
        direction = direction[1:-1]
        if name not in remotes:
            remotes[name] = dict()
        remotes[name][f"{direction}_url"] = url

    return {name: GitRemote(**kwargs) for name, kwargs in remotes.items()}


def git_current_branch(path: str = os.getcwd()) -> str:
    return git_out(["rev-parse", "--abbrev-ref", "HEAD"], path).strip()


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
        git_interactive(["init"], path)
        return cls.load(path)

    def status(self) -> None:
        git_interactive(["status"], self.path)

    # This dirty check is courtesy an answer on this StackOverflow post:
    #
    #    https://stackoverflow.com/questions/2657935/checking-for-a-dirty-index-or-untracked-files-with-git

    def dirty(self) -> bool:
        lines = git_out(["status", "--porcelain"], self.path).strip()
        return len(lines) > 0

    def add(self, what: str) -> None:
        git_interactive(["add", what], self.path)

    def commit(self, message: Optional[str] = None) -> None:
        argv = ["commit"]
        if message:
            argv += ["-m", message]
        git_interactive(argv, self.path)
