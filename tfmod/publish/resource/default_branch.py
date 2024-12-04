import traceback
from typing import Optional, Self

from tfmod.error import DefaultBranchError, GitError, GitHeadNotFoundError
from tfmod.git import git_get_config
from tfmod.io import logger
from tfmod.plan import may, Resource
from tfmod.publish.resource.git import GitResource
from tfmod.publish.resource.repository import RepositoryResource


class DefaultBranchResource(Resource[str]):
    name = "default_branch"

    def get(self: Self) -> Optional[str]:
        # We could check the local git repo for a set upstream - it would be
        # faster than checking the repo. But we need to pull this information
        # anyway, so we might as well just check the canonical source.

        logger.info("Checking repository for a default branch...")
        repo = may(RepositoryResource)

        if repo and repo.default_branch is not None:
            logger.info("Repository had a default branch")
            return repo.default_branch

        try:
            logger.info("Falling back to the local default branch...")
            default_branch = git_get_config("init.defaultbranch")
            if default_branch:
                logger.info("Local default branch configured")
                return default_branch
            return None
        except GitError:
            logger.info(traceback.format_exc())
            return None

    def validate(self: Self, resource: str) -> None:
        git = may(GitResource)

        if not git:
            logger.info("Git repository does not exist - not validating branch")
            return

        try:
            current_branch = git.current_branch()
        except GitHeadNotFoundError:
            return

        if resource != git.current_branch():
            raise DefaultBranchError(
                f"Branch {current_branch} is not the default branch ({resource})"
            )
