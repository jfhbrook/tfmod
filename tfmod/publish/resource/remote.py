from typing import Any, cast, Dict, Optional, Self, Tuple

from giturlparse import GitUrlParsed

from tfmod.error import DefaultBranchError, GhRemoteNotFoundError
from tfmod.io import logger
from tfmod.plan import must, Resource
from tfmod.publish.resource.git import GitResource
from tfmod.publish.resource.spec import SpecResource

Remote = Tuple[str, GitUrlParsed]


class RemoteResource(Resource[Remote]):
    name = "remote"

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
        actual = cast(Any, remote).owner

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

        # TODO: This check is for the default branch with respect to the git
        # repo - ie, if you called --set-upstream. A repo might not *have* a
        # default branch - but the github API should be able to tell us what
        # GitHub's default branch is,
        # by looking at the "default_branch" property on the repo.

        expected: Optional[str] = git.default_branch(remote)
        actual = git.current_branch

        if expected is None:
            return

        if expected != actual:
            raise DefaultBranchError(
                f"Branch {actual} is not the default branch ({expected})"
            )
