import os
import os.path
from pathlib import Path
from shutil import which

import toml

CONFIG_DIR: Path = Path(os.path.expanduser("~/.config/tfmod"))
PACKAGE_DIR: Path = Path(__file__).parent.parent
MODULES_DIR: Path = PACKAGE_DIR / "modules"

CONFIG_TFVARS: Path = CONFIG_DIR / "tfmod.tfvars"
MODULE_TFVARS: Path = Path(os.getcwd()) / "module.tfvars"

TFMOD_VERSION: str = "???"

with open(PACKAGE_DIR / "pyproject.toml", "r") as f:
    TFMOD_VERSION = toml.load(f)["project"]["version"]

TERRAFORM_BIN = which("terraform")
