from functools import cache
import os
from typing import cast, Dict, List, Optional

from github.Repository import Repository
from giturlparse import GitUrlParsed

from tfmod.action import Action, run_actions
from tfmod.error import (
    Error,
    GhRemoteNotFoundError,
    GitDirtyError,
    GitRepoNotFoundError,
    PublishError,
)
from tfmod.gh import get_gh_user, gh_client, gh_repo_create, load_gh_hosts_optional
from tfmod.git import GitRepo
from tfmod.io import logger
from tfmod.spec import Spec
from tfmod.terraform import Terraform
from tfmod.version import Version

#
# Hoo boy...
#
# TODO: It would be nice to have a real DAG language here.
#

#
# Fetch dependencies. Functions prefixed with "must" *must* return that
# dependency, and *should* be cached. Functions prefixed with "try" *may*
# return the dependency, and *must not* be cached.
#


@cache
def must_spec() -> Spec:
    """
    Validate and load the spec file. Must return a spec.
    """
    cmd = Terraform("spec").isolated_state().spec().auto_approve()
    cmd.run()

    spec = Spec.load()
    _validate_directory(spec.repo_name())
    return spec


def try_git() -> Optional[GitRepo]:
    """
    Try to load the git repository. Not cached.
    """

    try:
        repo = GitRepo.load()
        _validate_current_branch(repo)
        return repo
    except GitRepoNotFoundError as exc:
        logger.debug(str(exc))
        return None


@cache
def must_git() -> GitRepo:
    """
    Load the git repository. GitRepo must exist when this is called.
    """
    repo = GitRepo.load()
    _validate_current_branch(repo)
    return repo


def try_user() -> Optional[str]:
    """
    Optionally load the GitHub user from the "gh" cli's host files.
    """
    hosts = load_gh_hosts_optional()
    return get_gh_user(hosts)


@cache
def must_user() -> str:
    user = try_user()
    if not user:
        raise PublishError('GitHub user not found in "gh" CLI\'s configuration')
    return user


def try_repository() -> Optional[Repository]:
    try:
        return _must_repository()
    except Error:
        return None


@cache
def must_repository() -> Repository:
    return _must_repository()


def _must_repository() -> Repository:
    spec = must_spec()
    client = gh_client()
    return client.get_user(cast(str, spec.namespace)).get_repo(spec.repo_name())


def try_remote() -> Optional[GitUrlParsed]:
    try:
        return _must_remote()
    except Error as exc:
        logger.debug(str(exc))
        return None


@cache
def must_remote() -> GitUrlParsed:
    return _must_remote()


def _must_remote() -> GitUrlParsed:
    """
    Find which git remote points to GitHub. If none seem to, raise an exception.
    """
    spec = must_spec()
    git = must_git()

    remotes: Dict[str, GitUrlParsed] = {
        name: remote.parse() for name, remote in git.remotes.items()
    }

    remote: Optional[GitUrlParsed] = None

    if "origin" in remotes and remotes["origin"].platform == "github":
        remote = remotes["origin"]
    else:
        for name, rem in remotes.items():
            if name == "origin":
                break
            if rem.platform == "github":
                remote = rem
                break
    if not remote:
        raise GhRemoteNotFoundError("GitHub remote not found")

    _validate_github_remote(
        namespace=spec.namespace,
        name=spec.repo_name(),
        remote_namespace=remote.user,
        remote_name=remote.name,
    )

    return remote


#
# Actions. These functions return lists of Actions depending on whether
# their dependencies exist or not. These call "try" functions for tests, and
# call "must" functions when prior actions are expected to have resolved those
# entities.
#


def git_actions() -> List[Action]:
    """
    Attempt to load the git repository. If not found, return actions which should
    create the repository.
    """
    repo = try_git()

    if not repo:
        return [
            Action(type="+", name="git init", run=GitRepo.init),
            Action(type="+", name="git add .", run=lambda: must_git().add(".")),
            Action(type="+", name="git commit", run=lambda: must_git().commit),
        ]

    return []


# TODO: -force flag
def mop_actions() -> List[Action]:
    """
    Check the repository to see if it's dirty. If so, generate actions that
    would make it clean.
    """
    repo = try_git()

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


def remote_actions() -> List[Action]:
    """
    Try finding a current remote pointing to GitHub. If it can't be found or
    the repository doesn't exist, return actions that would create the GitHub
    repository (if necessary) and add it as a remote.
    """

    git = try_git()

    if not git:
        return _remote_actions()

    remote = try_remote()
    if not remote:
        return _remote_actions()
    else:
        return []


def _remote_actions() -> List[Action]:
    spec = must_spec()
    repo_name = spec.repo_name()

    # TODO: Pull this from... git config?
    git_protocol = "ssh"
    user = must_user()
    git_url = f"git@github.com:{user}/{repo_name}"

    actions: List[Action] = list()

    repo = try_repository()
    if not repo:
        actions.append(
            Action(
                type="+",
                name=f"gh repo create {repo_name}",
                run=lambda: gh_repo_create(repo_name),
            )
        )
    actions.append(
        Action(
            type="+",
            name=f"git remote add origin {git_url}",
            run=lambda: must_git().add_remote("origin", git_url),
        )
    )

    return actions


def description_actions() -> List[Action]:
    """
    Check if the spec description matches what's on GitHub. If it doesn't match
    (or the repository doesn't exist), return actions that would update
    the GitHub repository's description to match the spec.
    """

    spec = must_spec()
    repo = try_repository()
    if not repo:
        return _description_actions()
    else:
        if repo.description != spec.description:
            return _description_actions()
        return []


def _description_actions() -> List[Action]:
    spec = must_spec()
    repo = must_repository()

    return [
        Action(
            type="~",
            name="(edit GitHub repository description)",
            run=lambda: repo.edit(description=cast(str, spec.description)),
        )
    ]


def tag_and_push_actions(version: Version) -> List[Action]:
    """
    Return actions that would tag and push to git.
    """
    git = must_git()
    remote = must_remote().name
    branch = git.current_branch
    patch = f"{version.major}.{version.minor}.{version.patch}"
    minor = f"{version.major}.{version.minor}"
    major = str(version.major)

    return [
        Action(type="+", name=f"git tag {patch}", run=lambda: git.tag(patch)),
        Action(
            type="~", name=f"git tag {minor} -f", run=lambda: git.tag(minor, force=True)
        ),
        Action(
            type="~", name=f"git tag {major} -f", run=lambda: git.tag(major, force=True)
        ),
        Action(
            type="~",
            name=f"git push {remote} {branch} --tags",
            run=lambda: git.push(remote, branch, tags=True),
        ),
    ]


#
# Any tasks we need to do outside of actions.
#


def validate_module() -> None:
    """
    Validate that the module has the expected directory structure. Show
    warnings if this isn't the case.
    """
    pass


def is_package_available() -> bool:
    return False


def open_package_url() -> None:
    raise NotImplementedError("open_package_url")


def publish() -> None:
    spec = must_spec()
    version = Version.parse(cast(str, spec.version))

    validate_module()

    run_actions(
        git_actions()
        + mop_actions()
        + remote_actions()
        + description_actions()
        + tag_and_push_actions(version)
    )

    if not is_package_available():
        open_package_url()


#
# Validators for dependencies. These *must* be called by the relevant
# dependency fetchers, and *must* be cached. They may either take arguments
# or call "must" functions, whichever is more convenient.
#


@cache
def _validate_directory(name: str, path: str = os.getcwd()) -> None:
    """
    Validate that the directory name matches the spec. Show warnings if
    this isn't the case.
    """
    pass


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


def _validate_mopped() -> None:
    """
    Validate that the repository is not dirty. By the time this is called,
    actions should have been completed.
    """
    repo = must_git()
    if repo.dirty():
        raise GitDirtyError("All files must be committed to continue.")


@cache
def _validate_github_remote(
    namespace: str, name: str, remote_namespace: str, remote_name: str
) -> None:
    """
    Validate that the git remote matches the spec. Show warnings if
    this isn't the case. Cached to only warn once.
    """
    pass
