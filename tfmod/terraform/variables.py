from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import hcl2

from tfmod.terraform.value import Value

# Make the type checker happy
hcl: Any = hcl2


@dataclass
class Variable:
    """
    A Terraform variable
    """

    description: Optional[str] = None
    type: Optional[str] = None
    default: Optional[Value] = None


def load_variables(module: Path) -> Dict[str, Variable]:
    """
    Load the variables defined in a module
    """
    with open(module / "variables.tf", "r") as f:
        data: Dict[str, Any] = hcl.load(f)

    rv: Dict[str, Variable] = dict()

    for var in data["variable"]:
        items: List[Tuple[str, Any]] = list(var.items())
        assert len(items) == 1
        name, contents = items[0]

        rv[name] = Variable(
            description=contents.get("description", None),
            type=contents.get("type", None),
            default=contents.get("default", None),
        )

    return rv
