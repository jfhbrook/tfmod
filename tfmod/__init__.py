import os
import os.path
from pathlib import Path

CONFIG_DIR: Path = Path(os.path.expanduser("~/.config/tfmod"))
MODULES_DIR: Path = Path(__file__).parent / "modules"

CONFIG_TFVARS: Path = CONFIG_DIR / "tfmod.tfvars"
MODULE_TFVARS: Path = Path(os.getcwd()) / "module.tfvars"
