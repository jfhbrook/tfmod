from typing import Optional, Self

from tfmod.error import GitRepoNotFoundError
from tfmod.git import GitRepo
from tfmod.io import logger
from tfmod.plan import must, Resource
from tfmod.publish.resource.module import ModuleResource


class GitResource(Resource[GitRepo]):
    name = "git"

    def get(self: Self) -> Optional[GitRepo]:
        must(ModuleResource)
        try:
            repo = GitRepo.load()
            return repo
        except GitRepoNotFoundError as exc:
            logger.debug(str(exc))
            return None
