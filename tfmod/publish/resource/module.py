import os
import os.path
from pathlib import Path
from typing import Optional, Self

from tfmod.io import logger
from tfmod.plan import must, Resource
from tfmod.publish.resource.spec import SpecResource
from tfmod.validate import validate_readme


class ModuleResource(Resource[str]):
    name = "module"

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
