from dataclasses import dataclass
from typing import Dict, Optional


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
