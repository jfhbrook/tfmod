import shlex
from typing import cast, List

from tfmod.error import GitDirtyError
from tfmod.gh import gh_repo_create, gh_repo_description
from tfmod.git import GitRepo
from tfmod.plan import Action, apply, may, must, Plan
from tfmod.publish.resource.git import GitResource
from tfmod.publish.resource.module import ModuleResource
from tfmod.publish.resource.remote import RemoteResource
from tfmod.publish.resource.repository import RepositoryResource
from tfmod.publish.resource.spec import SpecResource
from tfmod.publish.resource.user import UserResource
from tfmod.publish.resource.version import VersionResource


def git_actions() -> List[Action]:
    """
    Attempt to load the git repository. If not found, return actions which should
    create the repository.
    """
    repo = may(GitResource)

    if not repo:
        return [
            Action(type="+", name="git init", run=GitRepo.init),
            Action(type="+", name="git add .", run=lambda: must(GitResource).add(".")),
            Action(type="+", name="git commit", run=lambda: must(GitResource).commit),
        ]

    return []


# TODO: -force flag
def mop_actions() -> List[Action]:
    """
    Check the repository to see if it's dirty. If so, generate actions that
    would make it clean.
    """
    repo = may(GitResource)

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

    git = may(GitResource)

    if not git:
        return _remote_actions()

    remote = may(RemoteResource)
    if not remote:
        return _remote_actions()
    else:
        return []


def _remote_actions() -> List[Action]:
    spec = must(SpecResource)
    repo_name = spec.repo_name()

    user = must(UserResource)
    remote_name = "origin"
    git_url = f"git@github.com:{user}/{repo_name}"

    actions: List[Action] = list()

    repo = may(RepositoryResource)
    if not repo:
        actions.append(
            Action(
                type="+",
                name=shlex.join(["gh", "repo", "create", repo_name]),
                run=lambda: gh_repo_create(repo_name),
            )
        )
    actions.append(
        Action(
            type="+",
            name=shlex.join(["git", "remote", "add", remote_name, git_url]),
            run=lambda: must(GitResource).add_remote(remote_name, git_url),
        )
    )

    return actions


def description_actions() -> List[Action]:
    """
    Check if the spec description matches what's on GitHub. If it doesn't match
    (or the repository doesn't exist), return actions that would update
    the GitHub repository's description to match the spec.
    """

    spec = must(SpecResource)
    repo = may(RepositoryResource)
    if not repo:
        return _description_actions()
    else:
        if repo.description != spec.description:
            return _description_actions()
        return []


def _description_actions() -> List[Action]:
    spec = must(SpecResource)
    description = cast(str, spec.description)

    return [
        Action(
            type="~",
            name=shlex.join(["gh", "repo", "edit", "--description", description]),
            run=lambda: gh_repo_description(description),
        )
    ]


def tag_and_push_actions() -> List[Action]:
    """
    Return actions that would tag and push to git.
    """
    git = must(GitResource)
    remote, _ = must(RemoteResource)
    version = must(VersionResource)

    branch = git.current_branch
    patch = f"{version.major}.{version.minor}.{version.patch}"
    minor = f"{version.major}.{version.minor}"
    major = str(version.major)

    return [
        # TODO: -force flag, and/or validate if this tag exists
        Action(type="+", name=f"git tag {patch} -f", run=lambda: git.tag(patch)),
        Action(
            type="~", name=f"git tag {minor} -f", run=lambda: git.tag(minor, force=True)
        ),
        Action(
            type="~", name=f"git tag {major} -f", run=lambda: git.tag(major, force=True)
        ),
        Action(
            type="~",
            name=f"git push {remote} {branch}",
            run=lambda: git.push(remote, branch),
        ),
        Action(
            type="~",
            name=f"git push {remote} --tags --force",
            run=lambda: git.push(remote, tags=True, force=True),
        ),
    ]


def is_package_available() -> bool:
    return False


def open_package_url() -> None:
    print(
        """To publish your package, go to:

    https://registry.terraform.io/github/create"""
    )


def publish() -> None:
    must(SpecResource)
    must(ModuleResource)

    plan: Plan = (
        git_actions()
        + mop_actions()
        + remote_actions()
        + description_actions()
        + tag_and_push_actions()
    )

    apply(plan)

    if not is_package_available():
        open_package_url()


def validate_mopped() -> None:
    """
    Validate that the repository is not dirty. By the time this is called,
    actions should have been completed.
    """
    repo = must(GitResource)
    if repo.dirty():
        raise GitDirtyError("All files must be committed to continue.")
