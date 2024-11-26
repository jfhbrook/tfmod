from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Self, Type

import hcl2

# Make the type checker happy
hcl: Any = hcl2

Script = List[str]


@dataclass
class Module:
    name: Optional[str]
    provider: Optional[str]
    version: Optional[str]
    description: Optional[str]

    scripts: Dict[str, Script]

    @classmethod
    def load(cls: Type[Self], path: Path = Path(os.getcwd())) -> Self:
        with open(path / "module.tfvars", "r") as f:
            var = hcl.load(f).get("module", dict())

        scripts: Dict[str, Script] = dict()

        if "scripts" in var:
            scripts = var.scripts
            assert type(scripts) == dict
            for name, script in scripts.items():
                assert type(script) == list
                scripts[name] = script

        return cls(
            name=var.get("name", None),
            provider=var.get("provider", None),
            version=var.get("version", None),
            description=var.get("description", None),
            scripts=scripts,
        )
