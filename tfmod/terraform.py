import os.path
from typing import Dict, List, Tuple

from tfmod import CONFIG_TFVARS, MODULE_TFVARS, MODULES_DIR


class TfCommand:
    def __init__(self, name: str, command: str) -> None:
        self.chdir: str = str(MODULES_DIR / name)
        self.command: str = command
        self._env: Dict[str, str] = dict()
        self.vars: Dict[str, str] = dict()
        self.var_flags: Dict[str, bool] = dict()
        self.var_files: List[str] = list()
        self._global_args: List[str] = list()
        self._command_args: List[str] = list()

    def env(self, name: str, value: str) -> None:
        self._env[name] = value

    def var(self, name: str, value: str) -> None:
        self.vars[name] = value

    def var_flag(self, name: str, value: bool) -> None:
        self.var_flags[name] = value

    def var_file(self, path: str) -> None:
        """
        Load a var file
        """
        self.var_files.append(path)

    def config(self) -> None:
        """
        Load TfMod's config
        """
        if os.path.isfile(CONFIG_TFVARS):
            self.var_file(str(CONFIG_TFVARS))

    def module(self) -> None:
        """
        Load the current module.tfvars
        """
        if os.path.isfile(MODULE_TFVARS):
            self.var_file(str(MODULE_TFVARS))

    def auto_approve(self) -> None:
        """
        Automatically approve the plan
        """
        self.var_flags["auto-approve"] = True

    def global_args(self, args: List[str]) -> None:
        """
        Add raw global arguments
        """
        self._global_args += args

    def command_args(self, args: List[str]) -> None:
        """
        Add raw command arguments
        """
        self._command_args += args

    def build(self) -> Tuple[List[str], Dict[str, str]]:
        """
        Build argv
        """

        args: List[str] = []
        args.append(f"-chdir={self.chdir}")
        args += self._global_args
        args.append(self.command)

        for file in self.var_files:
            args.append(f"-var-file={file}")

        for name, value in self.vars.items():
            args.append(f"-var")
            args.append(f"{name}={value}")

        for name, value in self.var_flags.items():
            args.append(f"-var")
            args.append(f"{name}={'true' if value else 'false'}")

        return args + self._command_args, self._env

    def run(self) -> None:
        """
        Run the Terraform command
        """
        args, env = self.build()
        print(["terraform"] + args, env)
