import os
import os.path
from pathlib import Path
from shutil import which

import toml

from tfmod.error import Error

CONFIG_DIR: Path = Path(os.path.expanduser("~/.config/tfmod"))
PACKAGE_DIR: Path = Path(__file__).parent.parent
MODULES_DIR: Path = PACKAGE_DIR / "modules"

CONFIG_TFVARS: Path = CONFIG_DIR / "tfmod.tfvars"
MODULE_TFVARS: Path = Path(os.getcwd()) / "module.tfvars"

TFMOD_VERSION: str = "???"

with open(PACKAGE_DIR / "pyproject.toml", "r") as f:
    TFMOD_VERSION = toml.load(f)["project"]["version"]

STATE_DIR: Path = Path(os.path.expanduser("~/.local/state/tfmod"))

_terraform_bin = which("terraform")

if _terraform_bin is None:
    raise Error('"terraform" could not be found.')

TERRAFORM_BIN: str = _terraform_bin

GH_CONFIG_DIR: Path = Path(os.path.expanduser("~/.config/gh/"))
