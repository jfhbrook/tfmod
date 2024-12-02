from dataclasses import dataclass
import os
import re
import shlex
from subprocess import CalledProcessError
from typing import Dict, List, Literal, Optional

import giturlparse

from tfmod.constants import GIT_BIN
from tfmod.error import GitError
from tfmod.process import run_interactive, run_out, run_test

Direction = Literal["fetch"] | Literal["push"]


def git_out(command: List[str], path: str = os.getcwd()) -> str:
    argv = [GIT_BIN] + command
    try:
        return run_out(argv, cwd=path)
    except CalledProcessError as exc:
        raise GitError(
            f'"{shlex.join(argv)}" exited unsuccessfully (status: {exc.returncode})'
        )


def git_test(command: List[str], path: str = os.getcwd()) -> bool:
    return run_test([GIT_BIN] + command, cwd=path)


def git_interactive(command: List[str], path: str = os.getcwd()) -> None:
    try:
        return run_interactive([GIT_BIN] + command, cwd=path)
    except CalledProcessError as exc:
        raise GitError(str(exc))


@dataclass
class GitRemote:
    # NOTE: It may be possible that either of these is optional. But I don't
    # see any documentation for that in git and haven't seen it in practice.
    fetch_url: str
    push_url: str

    def parse(self, direction: Direction = "push") -> giturlparse.GitUrlParsed:
        url = self.push_url if direction == "push" else self.fetch_url
        # TODO: Error handling
        return giturlparse.parse(url)


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
    def init(cls, path: str = os.getcwd()) -> None:
        git_interactive(["init"], path)

    def status(self) -> None:
        git_interactive(["status"], self.path)

    def dirty(self) -> bool:
        # This dirty check is courtesy an answer on this StackOverflow post:
        #
        #     https://stackoverflow.com/questions/2657935/checking-for-a-dirty-index-or-untracked-files-with-git
        lines = git_out(["status", "--porcelain"], self.path).strip()
        return len(lines) > 0

    def default_branch(self, remote: str) -> Optional[str]:
        # This check is courtesy a different StackOverflow post:
        #
        #     https://stackoverflow.com/questions/28666357/how-to-get-default-git-branch
        out = git_out(["remote", "show", remote])

        search = re.search(r"^\s+HEAD branch: (.*)$", out, re.MULTILINE)
        if not search:
            return None
        return search.group(1)

    def add(self, what: str) -> None:
        git_interactive(["add", what], self.path)

    def commit(self, message: Optional[str] = None) -> None:
        argv = ["commit"]
        if message:
            argv += ["-m", message]
        git_interactive(argv, self.path)

    def add_remote(self, name: str, url: str) -> None:
        git_interactive(["remote", "add", name, url], self.path)

    def tag(self, name: str, force=False) -> None:
        argv = ["tag", name]
        if force:
            argv.append("-f")
        git_interactive(argv)

    def push(
        self, remote: str, branch: Optional[str] = None, tags=False, force=False
    ) -> None:
        argv = ["push", remote]
        if branch:
            argv.append(branch)
        if tags:
            argv.append("--tags")
        if force:
            argv.append("--force")
        git_interactive(argv)
