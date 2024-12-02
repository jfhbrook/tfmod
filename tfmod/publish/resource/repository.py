from typing import cast, Optional, Self

from github.GithubException import UnknownObjectException
from github.Repository import Repository

from tfmod.gh import gh_client
from tfmod.io import logger
from tfmod.plan import must, Resource
from tfmod.publish.resource.spec import SpecResource


class RepositoryResource(Resource[Repository]):
    name = "repository"

    def get(self: Self) -> Optional[Repository]:
        spec = must(SpecResource)
        client = gh_client()

        try:
            return client.get_user(cast(str, spec.namespace)).get_repo(spec.repo_name())
        except UnknownObjectException as exc:
            logger.debug(str(exc))
            return None
