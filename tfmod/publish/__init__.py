import shlex
import textwrap
import traceback
from typing import Any, cast, Dict, List, Optional
import webbrowser

from tf_registry import RegistryClient, RegistryError

from tfmod.error import DefaultBranchError, GhError, GitDirtyError
from tfmod.gh import gh_git_protocol, gh_repo_create, gh_repo_description
from tfmod.git import GitRepo
from tfmod.io import logger
from tfmod.plan import Action, apply, may, must, Plan
from tfmod.publish.resource.default_branch import DefaultBranchResource
from tfmod.publish.resource.git import GitResource
from tfmod.publish.resource.module import ModuleResource
from tfmod.publish.resource.remote import RemoteResource
from tfmod.publish.resource.repository import RepositoryResource
from tfmod.publish.resource.spec import SpecResource
from tfmod.publish.resource.user import UserResource
from tfmod.publish.resource.version import VersionResource
from tfmod.spec import Spec


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


def mop_actions(force: bool) -> List[Action]:
    """
    Check the repository to see if it's dirty. If so, generate actions that
    would make it clean.
    """
    repo = may(GitResource)

    if not repo or not repo.dirty() or force:
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
    public = not spec.private

    protocol: str = "ssh"

    def default_ssh():
        nonlocal protocol

        logger.warn(
            "Could not discover GitHub git protocol", "Protocol will default to SSH."
        )
        protocol = "ssh"

    try:
        protocol = gh_git_protocol()
    except GhError:
        logger.info(traceback.format_exc())
        default_ssh()

    if protocol not in {"https", "ssh"}:
        default_ssh()

    if protocol == "ssh":
        git_url = f"git@github.com:{user}/{repo_name}.git"
    else:
        git_url = f"https://github.com/{user}/{repo_name}.git"

    actions: List[Action] = list()

    repo = may(RepositoryResource)
    if not repo:
        actions.append(
            Action(
                type="+",
                name=shlex.join(
                    [
                        "gh",
                        "repo",
                        "create",
                        repo_name,
                        "--public" if public else "--private",
                    ]
                ),
                run=lambda: gh_repo_create(repo_name, public=public),
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


def tag_and_push_actions(force: bool) -> List[Action]:
    """
    Return actions that would tag and push to git.
    """
    version = must(VersionResource)
    git = may(GitResource)
    rem = may(RemoteResource)

    default_branch: Optional[str] = None

    try:
        default_branch = may(DefaultBranchResource)
    except DefaultBranchError:
        if not force:
            raise

    if rem:
        remote, _ = rem
    else:
        remote = "origin"

    if default_branch:
        branch = default_branch
    elif git is None:
        branch = default_branch if default_branch else "main"
    else:
        branch = git.current_branch()

    patch = f"{version.major}.{version.minor}.{version.patch}"
    minor = f"{version.major}.{version.minor}"
    major = str(version.major)

    return [
        # TODO: -force flag, and/or validate if this tag exists
        Action(
            type="+",
            name=f"git tag {patch}" + (" -f" if force else ""),
            run=lambda: must(GitResource).tag(patch, force=force),
        ),
        Action(
            type="~",
            name=f"git tag {minor} -f",
            run=lambda: must(GitResource).tag(minor, force=True),
        ),
        Action(
            type="~",
            name=f"git tag {major} -f",
            run=lambda: must(GitResource).tag(major, force=True),
        ),
        # TODO: If repo is new, add --set-upstream flag
        Action(
            type="~",
            name=f"git push {remote} {branch}" + (" --force" if force else ""),
            run=lambda: must(GitResource).push(remote, branch, force=force),
        ),
        Action(
            type="~",
            name=f"git push {remote} --tags --force",
            run=lambda: must(GitResource).push(remote, tags=True, force=True),
        ),
    ]


def is_unpublished(spec: Spec) -> bool:
    namespace = cast(str, spec.namespace)
    name = cast(str, spec.name)
    provider = cast(str, spec.provider)
    try:
        client = RegistryClient()
        # Hoping this is a relatively quick check, since the payloads are
        # virtually nonexistent
        client.latest_download_url(namespace, name, provider)
    except RegistryError as exc:
        # Not found, baby!
        if exc.code == 404:
            return True

        # Don't block, just return False
        logger.debug(f"Terraform Registry API error: {exc}")
        logger.warn(
            f"Terraform Registry API failed with code {exc.code}:",
            textwrap.dedent(
                """
            The Terraform Registry may be having issues and may work in the future.
            """
            ).strip(),
        )
    return False


CREATE_PACKAGE_URL = "https://registry.terraform.io/github/create"


def open_package_url() -> None:
    print(
        "Your module is available on GitHub, but not published to the "
        "Terraform Registry."
    )
    print("To publish your package, visit:")
    print("")
    print(f"    {CREATE_PACKAGE_URL}")
    print("")

    # TODO: Disable opening URL in core config
    if webbrowser.open_new_tab(CREATE_PACKAGE_URL):
        print(f"{CREATE_PACKAGE_URL} has automatically been opened in your browser.")

    print("(To disable this check, set private = true in module.tfvars)")


def publish(args: Dict[str, Any]) -> None:
    force: bool = args["force"]
    auto_approve = args["auto_approve"]
    spec = must(SpecResource)
    must(ModuleResource)

    plan: Plan = (
        git_actions()
        + mop_actions(force)
        + remote_actions()
        + description_actions()
        + tag_and_push_actions(force)
    )

    apply(plan, auto_approve=auto_approve)

    if not spec.private and is_unpublished(spec):
        open_package_url()
    else:
        logger.ok("Your module has been published!")


def validate_mopped() -> None:
    """
    Validate that the repository is not dirty. By the time this is called,
    actions should have been completed.
    """
    repo = must(GitResource)
    if repo.dirty():
        raise GitDirtyError("All files must be committed to continue.")
