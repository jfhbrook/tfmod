from typing import cast, Optional, Self

from tfmod.plan import must, Resource
from tfmod.publish.resource.spec import SpecResource
from tfmod.version import Version


class VersionResource(Resource[Version]):
    def get(self: Self) -> Optional[Version]:
        spec = must(SpecResource)

        return Version.parse(cast(str, spec.version))
