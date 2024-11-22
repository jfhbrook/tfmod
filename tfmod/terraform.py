import os.path
from typing import List

from tfmod import CONFIG_TFVARS, MODULE_TFVARS, MODULES_DIR


def run_terraform(module: str, args: List[str]) -> None:
    module = str(MODULES_DIR / module)
    tf_args = [f"-chdir={module}"]

    if os.path.isfile(CONFIG_TFVARS):
        tf_args.append(f"-var-file={CONFIG_TFVARS}")

    tf_args.append(f"-var-file={MODULE_TFVARS}")

    tf_args += args

    print(["terraform"] + tf_args)
