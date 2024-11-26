import os.path
from pathlib import Path
from subprocess import Popen
from time import sleep
from typing import Dict, List, Mapping, Optional, Self, Tuple

from tfmod.constants import CONFIG_TFVARS, MODULE_TFVARS, MODULES_DIR, TERRAFORM_BIN
from tfmod.error import TerraformError
from tfmod.terraform.value import dump_value, Value
from tfmod.terraform.variables import load_variables, prompt_var, Variable

PathLike = Path | str


class Terraform:
    def __init__(
        self,
        name: str,
        command: str = "apply",
        interval: float = 0.1,
        timeout: Optional[float] = None,
    ) -> None:
        self._module: Path = MODULES_DIR / name
        self._command: str = command
        self._interval: float = interval
        self._timeout: Optional[float] = timeout
        self._env: Dict[str, str] = dict()
        self._vars: Dict[str, str] = dict()
        self._prompt_vars: Dict[str, Variable] = dict()
        self._var_files: List[str] = list()
        self._args: List[str] = list()

    def env(self, name: str, value: Value) -> Self:
        self._env[name] = dump_value(value)
        return self

    def var(self, name: str, value: Value) -> Self:
        self._vars[name] = dump_value(value)
        return self

    def prompt_var(
        self,
        name: str,
        description: Optional[str] = None,
        default: Optional[Value] = None,
    ) -> Self:
        self._prompt_vars[name] = Variable(description=description, default=default)
        return self

    def var_file(self, path: PathLike) -> Self:
        """
        Load a var file
        """
        self._var_files.append(str(path))
        return self

    def config(self) -> Self:
        """
        Load TfMod's config
        """
        if os.path.isfile(CONFIG_TFVARS):
            self.var_file(str(CONFIG_TFVARS))
        return self

    def module(self) -> Self:
        """
        Load the current module.tfvars
        """
        if os.path.isfile(MODULE_TFVARS):
            self.var_file(str(MODULE_TFVARS))
        return self

    def auto_approve(self) -> Self:
        """
        Automatically approve the plan
        """
        self._args += ["-auto-approve"]
        return self

    def args(self, args: List[str]) -> Self:
        """
        Add raw arguments
        """
        self._args += args
        return self

    def _prompt(self) -> None:
        vars = load_variables(self._module)
        for name, var in self._prompt_vars.items():
            description: Optional[str] = var.description
            default = var.default

            if name in vars and vars[name].description:
                description = vars[name].description
            if name in vars and vars[name].default:
                default = vars[name].default

            self._vars[name] = dump_value(
                prompt_var(name, description=description, default=default)
            )

    def build(self) -> Tuple[List[str], Dict[str, str]]:
        """
        Build argv
        """

        self._prompt()

        args: List[str] = []
        args.append(f"-chdir={self._module}")
        args.append(self._command)

        for file in self._var_files:
            args.append(f"-var-file={file}")

        for name, value in self._vars.items():
            args.append(f"-var")
            args.append(f"{name}={value}")

        return args + self._args, self._env

    def _finish(self, exit_code: int) -> None:
        if exit_code:
            raise TerraformError(exit_code)

    def run(self, env: Mapping[str, str] = os.environ) -> None:
        """
        Run the Terraform command
        """
        args, _env = self.build()
        _env = dict(env, **_env)

        with Popen([TERRAFORM_BIN] + args, env=_env) as proc:
            try:
                while True:
                    exit_code: Optional[int] = proc.poll()
                    if exit_code is not None:
                        self._finish(exit_code)
                        return
                    sleep(self._interval)
            except KeyboardInterrupt:
                exit_code = proc.wait(self._timeout)
                self._finish(proc.wait(timeout=self._timeout))
                return
