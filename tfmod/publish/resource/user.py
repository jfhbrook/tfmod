from typing import Optional, Self

from tfmod.gh import get_gh_user, load_gh_hosts_optional
from tfmod.plan import Resource


class UserResource(Resource[str]):
    name = "user"

    def get(self: Self) -> Optional[str]:
        hosts = load_gh_hosts_optional()
        return get_gh_user(hosts)
