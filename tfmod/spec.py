from collections import defaultdict
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Self, Type

import hcl2

from tfmod.error import SpecValueError
from tfmod.io import logger

# Make the type checker happy
hcl: Any = hcl2

Script = List[str]


def warn_type(variable: str, type: str) -> None:
    a = "a"
    if type[0] in "aeiou":
        a = "an"
    logger.warn(
        f"Invalid value for {variable}",
        f"""This value is not compatible with the module's type
constraint: {a} {type} is required.""",
    )


def warn_attribute(variable: str, attribute: str) -> None:
    logger.warn(
        f"Invalid value for {variable}",
        f"""This value is not compatible with the module's type
constraint: attribute "{attribute}" is required.""",
    )


class WarnScript:
    def __init__(self) -> None:
        self._warned: Dict[str, bool] = defaultdict(lambda: False)

    def __call__(self, name: str) -> None:
        if self._warned[name]:
            return
        self._warned[name] = True
        warn_type(f"{name} script", "list(string)")


@dataclass
class Spec:
    name: Optional[str]
    namespace: Optional[str]
    provider: Optional[str]
    version: Optional[str]
    description: Optional[str]

    scripts: Dict[str, Script]

    @classmethod
    def load_optional(
        cls: Type[Self], path: Path = Path(os.getcwd())
    ) -> Optional[Self]:
        try:
            return cls.load(path)
        except FileNotFoundError as exc:
            logger.debug(str(exc))
            return None

    @classmethod
    def load(cls: Type[Self], path: Path = Path(os.getcwd())) -> Self:
        with open(path / "module.tfvars", "r") as f:
            var = hcl.load(f).get("module", None)

        if not var:
            warn_type("module", "object")
            return cls(
                name=None,
                namespace=None,
                provider=None,
                version=None,
                description=None,
                scripts=dict(),
            )

        scripts: Dict[str, Script] = dict()

        warn_script = WarnScript()

        if "scripts" in var:
            defined_scripts = var["scripts"]
            if type(defined_scripts) is not dict:
                warn_type("scripts", "map")
            else:
                for name, defined_script in defined_scripts.items():
                    if type(defined_script) is not list:
                        warn_script(name)
                    else:
                        script: List[str] = list()
                        for line in defined_script:
                            if type(line) is not str:
                                warn_script(name)
                            script.append(str(line))
                        scripts[name] = script

        return cls(
            name=var.get("name", None),
            namespace=var.get("namespace", None),
            provider=var.get("provider", None),
            version=var.get("version", None),
            description=var.get("description", None),
            scripts=scripts,
        )

    def repo_name(self) -> str:
        if not self.provider:
            raise SpecValueError("Module provider not specified")
        if not self.name:
            raise SpecValueError("Module name not specified")
        return f"terraform-{self.provider}-{self.name}"


Version = Any


def parse_version(spec: Spec) -> Version:
    raise NotImplementedError("parse_version(spec)")
