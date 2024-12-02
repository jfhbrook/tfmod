import os
import os.path
from pathlib import Path
import shlex
from typing import cast, Dict, List, Optional, Self, Tuple

from github.GithubException import UnknownObjectException
from github.Repository import Repository
from giturlparse import GitUrlParsed

from tfmod.error import (
    DefaultBranchError,
    GhRemoteNotFoundError,
    GitDirtyError,
    GitRepoNotFoundError,
)
from tfmod.gh import (
    get_gh_user,
    gh_client,
    gh_repo_create,
    gh_repo_description,
    load_gh_hosts_optional,
)
from tfmod.git import GitRepo
from tfmod.io import logger
from tfmod.plan import Action, apply, may, must, Plan, Resource
from tfmod.spec import Spec
from tfmod.terraform import Terraform
from tfmod.validate import validate_readme
from tfmod.version import Version

# The Terraform Registry seems to only allow modules to be published which
# use recognized providers. That surely includes official providers. It
# *may* also include partner providers, though listing those manually is a
# much bigger chore.
OFFICIAL_PROVIDERS = {
    "aws",
    "azurerm",
    "google",
    "kubernetes",
    "alicloud",
    "oracle",
    "ad",
    "archive",
    "assert",
    "awscc",
    "azuread",
    "azurestack",
    "boundary",
    "cloudinit",
    "consul",
    "dns",
    "external",
    "google-beta",
    "googleworkspace",
    "hcp",
    "hcs",
    "helm",
    "http",
    "local",
    "nomad",
    "null",
    "opc",
    "oraclepaas",
    "random",
    "salesforce",
    "template",
    "tfe",
    "tfmigrate",
    "time",
    "tls",
    "vault",
    "vsphere",
}

#
# Resources.
#


class SpecResource(Resource[Spec]):
    def get(self: Self) -> Optional[Spec]:
        # We validate with Terraform before trying to load. This is because
        # we want to see Terraform errors prior to choking on the load.
        self._pre_validate()
        return Spec.load()

    def _pre_validate(self: Self) -> None:
        cmd = Terraform("spec").isolated_state().spec().auto_approve()
        cmd.run()

    def validate(self, resource: Spec) -> None:
        # This SHOULD get handled during Terraform validation.
        assert resource.provider

        if resource.provider not in OFFICIAL_PROVIDERS and not resource.private:
            logger.warn(
                title=f"${resource.provider} is not an official provider",
                message="""If the Terraform Registry does not recognize the
                provider, it may not allow you to publish it.

                To quiet this message, set the "private" field in your
                module.tfvars file.
                """,
            )


class ModuleResource(Resource[str]):
    def get(self: Self) -> Optional[str]:
        return os.getcwd()

    def validate(self: Self, resource: str) -> None:
        self._validate_directory_name(resource)
        validate_readme(resource)

    def _validate_directory_name(self: Self, resource: str) -> None:
        spec = must(SpecResource)
        expected = spec.repo_name()
        actual = Path(resource).name

        if expected != actual:
            logger.warn(
                title=f'Directory name "{actual}" does not match module.tfvars',
                message=f""""The project should to be named \"{expected}\", in order
                to match the conventions of the Terraform registry.""",
            )


class GitResource(Resource[GitRepo]):
    def get(self: Self) -> Optional[GitRepo]:
        must(ModuleResource)
        try:
            repo = GitRepo.load()
            return repo
        except GitRepoNotFoundError as exc:
            logger.debug(str(exc))
            return None


class UserResource(Resource[str]):
    def get(self: Self) -> Optional[str]:
        hosts = load_gh_hosts_optional()
        return get_gh_user(hosts)


class RepositoryResource(Resource[Repository]):
    def get(self: Self) -> Optional[Repository]:
        spec = must(SpecResource)
        client = gh_client()

        try:
            return client.get_user(cast(str, spec.namespace)).get_repo(spec.repo_name())
        except UnknownObjectException as exc:
            logger.debug(str(exc))
            return None


Remote = Tuple[str, GitUrlParsed]


class RemoteResource(Resource[Remote]):
    def get(self: Self) -> Optional[Remote]:
        git = must(GitResource)

        remotes: Dict[str, GitUrlParsed] = {
            name: remote.parse() for name, remote in git.remotes.items()
        }

        remote: Optional[GitUrlParsed] = None
        remote_name: str = ""

        if "origin" in remotes and remotes["origin"].platform == "github":
            remote = remotes["origin"]
            remote_name = "origin"
        else:
            for name, rem in remotes.items():
                if rem.platform == "github":
                    remote = rem
                    remote_name = name
                    break
        if not remote:
            raise GhRemoteNotFoundError("GitHub remote not found")

        return remote_name, remote

    def validate(self: Self, resource: Remote) -> None:
        self._validate_namespace(resource)
        self._validate_name(resource)
        self._validate_default_branch(resource)

    def _validate_namespace(self: Self, resource: Remote) -> None:
        _, remote = resource
        spec = must(SpecResource)

        expected = cast(str, spec.namespace)
        actual = remote.user

        if expected != actual:
            logger.warn(
                title=f'GitHub namespace "{actual}" does not match ' "module.tfvars",
                message=f'The expected namespace is "{expected}".',
            )

    def _validate_name(self: Self, resource: Remote) -> None:
        _, remote = resource
        spec = must(SpecResource)

        expected = spec.repo_name()
        actual = remote.name

        if expected != actual:
            logger.warn(
                title=f'Repository name "{actual}" does not match module.tfvars',
                message=f""""The project should to be named \"{expected}\", in
                order to match the conventions of the Terraform registry.""",
            )

    def _validate_default_branch(self: Self, resource: Remote) -> None:
        remote, _ = resource
        git = must(GitResource)

        expected = git.default_branch(remote)
        actual = git.current_branch

        if expected != actual:
            raise DefaultBranchError(
                f"Branch {actual} is not the default branch ({expected})"
            )


#
# Actions.
#


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


def tag_and_push_actions(version: Version) -> List[Action]:
    """
    Return actions that would tag and push to git.
    """
    git = must(GitResource)
    remote, _ = must(RemoteResource)

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
    print(
        """To publish your package, go to:

    https://registry.terraform.io/github/create"""
    )


def publish() -> None:
    spec = must(SpecResource)
    version = Version.parse(cast(str, spec.version))

    validate_module()

    plan: Plan = (
        git_actions()
        + mop_actions()
        + remote_actions()
        + description_actions()
        + tag_and_push_actions(version)
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
