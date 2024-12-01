from functools import cache
import os
from typing import Callable, cast, Dict, List, Optional, Tuple, TypeVar

from github import UnknownObjectException
from github.Repository import Repository
from giturlparse import GitUrlParsed

from tfmod.action import Action, run_actions
from tfmod.error import (
    ApprovalInterruptError,
    Error,
    GhRemoteNotFoundError,
    GitDirtyError,
    GitRepoNotFoundError,
)
from tfmod.gh import get_gh_user, gh_client, gh_repo_create, load_gh_hosts_optional
from tfmod.git import GitRepo
from tfmod.io import logger
from tfmod.spec import Spec
from tfmod.terraform import Terraform
from tfmod.version import Version

T = TypeVar("T")
Lazy = Callable[[], T]


def load_spec() -> Spec:
    """
    Validate and load the spec file
    """
    cmd = Terraform("spec").isolated_state().spec().auto_approve()
    cmd.run()

    spec = Spec.load()
    _validate_directory(spec.repo_name())
    return spec


@cache
def _validate_directory(name: str, path: str = os.getcwd()) -> None:
    """
    Validate that the directory name matches the spec. Show warnings if
    this isn't the case.
    """
    pass


def validate_module() -> None:
    """
    Validate that the module has the expected directory structure. Show
    warnings if this isn't the case.
    """
    pass


def try_git() -> Tuple[Optional[GitRepo], List[Action]]:
    """
    Attempt to load the git repository. If not found, return actions which should
    create the repository.
    """
    try:
        repo = GitRepo.load()
        _validate_current_branch(repo)
    except GitRepoNotFoundError:
        @cache
        def lazy_repo() -> GitRepo:
            return GitRepo.load()

        return None, [
            Action(type="+", name="git init", run=GitRepo.init),
            Action(type="+", name="git add .", run=lambda: lazy_repo().add(".")),
            Action(type="+", name="git commit", run=lambda: lazy_repo().commit),
        ]

    return repo, []


@cache
def load_git() -> GitRepo:
    """
    Load the git repository. By the time this is called, actions should have
    been completed.
    """
    repo = GitRepo.load()
    _validate_current_branch(repo)
    return repo


def _validate_current_branch(repo: GitRepo) -> None:
    """
    Validate that the current branch is the main branch. Raise an Error if
    this is not the case, unless forced.
    """
    # Needs some reliable-ish way to detect what the main branch is. This will
    # either be through configuration (in module.tfvars or in main config) or
    # detected via something like:
    #
    #     https://stackoverflow.com/questions/28666357/how-to-get-default-git-branch
    pass


# TODO: -force flag
def mop(repo: Optional[GitRepo]) -> List[Action]:
    """
    Check the repository to see if it's dirty. If so, generate actions that
    would make it clean.
    """
    if not repo or not repo.dirty():
        # If the repo doesn't exist, we'll do these tasks during the git init.
        # If it's clean, then we don't have anything to do.
        return []

    print("Repository contains uncommitted changes:")
    repo.status()

    actions = [
        Action(type="~", name="git add .", run=lambda: repo.add(".")),
        Action(type="~", name="git commit", run=repo.commit),
    ]

    return actions


def validate_mopped() -> None:
    """
    Validate that the repository is not dirty. By the time this is called,
    actions should have been completed.
    """
    repo = load_git()
    if repo.dirty():
        raise GitDirtyError("All files must be committed to continue.")


def github_remote(spec: Spec, git: GitRepo) -> GitUrlParsed:
    """
    Find which git remote points to GitHub. If none seem to, raise an exception.
    """
    remotes: Dict[str, GitUrlParsed] = {
        name: remote.parse() for name, remote in git.remotes.items()
    }

    remote: Optional[GitUrlParsed] = None

    if "origin" in remotes and remotes["origin"].platform == "github":
        remote = remotes["origin"]
    else:
        for name, rem in remotes.items():
            if name == "origin":
                continue
            if rem.platform == "github":
                remote = rem
    if not remote:
        raise GhRemoteNotFoundError("GitHub remote not found")

    _validate_github_remote(
        namespace=spec.namespace,
        name=spec.repo_name(),
        remote_namespace=remote.user,
        remote_name=remote.name,
    )

    return remote


@cache
def _validate_github_remote(
    namespace: str, name: str, remote_namespace: str, remote_name: str
) -> None:
    """
    Validate that the git remote matches the spec. Show warnings if
    this isn't the case. Cached to only warn once.
    """
    pass


def _gh_user() -> Optional[str]:
    """
    Optionally load the GitHub user from the "gh" cli's host files.
    """
    hosts = load_gh_hosts_optional()
    return get_gh_user(hosts)


@cache
def _github_repo(user: str, name: str) -> Repository:
    """
    Get the GitHub repository. Cached as it's called both to check for
    existence and to access the description.
    """
    client = gh_client()
    return client.get_user(user).get_repo(name)


def github_repo(spec: Spec) -> Repository:
    """
    Get the GitHub repository.
    """
    return _github_repo(spec.namespace, spec.repo_name())


def _github_remote_actions(spec: Spec, git: Lazy[GitRepo]) -> List[Action]:
    """
    Generate actions which would create the GitHub repository (if necessary)
    and add it as a remote.
    """

    name = spec.repo_name()

    # TODO: Pull this from... git config?
    git_protocol = "ssh"
    gh_user = _gh_user()
    if not gh_user:
        # TODO: Better error
        raise Error("Need user to continue")

    git_url = f"git@github.com:{gh_user}/{name}"

    actions: List[Action] = list()

    try:
        github_repo(spec)
    except UnknownObjectException:
        actions.append(
            Action(
                type="+",
                name=f"gh repo create {name}",
                run=lambda: gh_repo_create(name),
            )
        )
    actions.append(
        Action(
            type="+",
            name=f"git remote add origin {git_url}",
            run=lambda: git().add_remote("origin", git_url),
        )
    )

    return actions


def try_github_remote(
    spec: Spec, git: Optional[GitRepo]
) -> Tuple[Optional[GitUrlParsed], List[Action]]:
    """
    Try finding a current remote pointing to GitHub. If it can't be found or
    the repository doesn't exist, return actions that would create the GitHub
    repository (if necessary) and add it as a remote.
    """

    def lazy_git() -> GitRepo:
        nonlocal git
        if not git:
            git = GitRepo.load()
        return git

    if not git:
        return None, _github_remote_actions(spec, lazy_git)

    try:
        remote = github_remote(spec, git)
    except GhRemoteNotFoundError as exc:
        logger.info(str(exc))
        return None, _github_remote_actions(spec, lazy_git)
    else:
        return remote, []


def update_description(spec: Spec) -> List[Action]:
    """
    Check if the spec description matches what's on GitHub. If it doesn't match
    (or the repository doesn't exist), return actions that would update
    the GitHub repository's description to match the spec.
    """

    try:
        repo = github_repo(spec)
    except UnknownObjectException:
        return _update_description(spec)
    else:
        if repo.description != spec.description:
            return _update_description(spec)
        return []


def _update_description(spec: Spec) -> List[Action]:
    """
    Return description actions, given we know they're required.
    """
    def lazy_github():
        return github_repo(spec)

    actions: List[Action] = list()

    raise NotImplementedError("description_actions")


def tag_and_push(version: Version) -> List[Action]:
    """
    Return actions that would tag and push to git.
    """
    # silent action:
    # validate_mopped()
    # lazy_repo = load_git
    # lazy_remote = lambda: github_remote(spec, load_git())
    raise NotImplementedError("tag_and_push")


def is_package_available() -> bool:
    return False


def open_package_url() -> None:
    raise NotImplementedError("open_package_url")


def publish() -> None:
    spec = load_spec()
    version = Version.parse(cast(str, spec.version))

    validate_module()

    git, git_actions = try_git()
    mop_actions = mop(git)
    _, remote_actions = try_github_remote(spec, git)
    description_actions = update_description(spec)
    push_actions = tag_and_push(version)

    run_actions(git_actions + mop_actions + remote_actions + description_actions + push_actions)

    if not is_package_available():
        open_package_url()
