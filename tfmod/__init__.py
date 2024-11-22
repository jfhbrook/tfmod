import os
from pathlib import Path

MODULES_DIR: Path = Path(__file__).parent / "modules"
MODULE_TFVARS = Path(os.getcwd()) / "module.tfvars"
