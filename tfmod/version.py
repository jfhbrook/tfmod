from dataclasses import dataclass
from typing import Self, Type


@dataclass
class Version:
    """
    A simplified semantic version. Hashicorp says they use semantic
    versioning, but they don't advertise support of the full spec.
    """

    major = int
    minor = int
    semver = int

    @classmethod
    def parse(cls: Type[Self], version: str) -> Self:
        splitted = version.split(".")
        return cls(*splitted)
