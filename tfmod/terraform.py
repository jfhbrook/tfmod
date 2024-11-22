from typing import List

from tfmod import MODULE_TFVARS, MODULES_DIR


def run_terraform(module: str, args: List[str]) -> None:
    module = str(MODULES_DIR / module)
    tf_args = [f"-chdir={module}", f"-var-file={MODULE_TFVARS}"]
    tf_args += args
    print(["terraform"] + tf_args)
