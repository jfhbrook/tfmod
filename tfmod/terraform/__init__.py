from contextlib import contextmanager
import os
import os.path
from pathlib import Path
import shutil
from subprocess import Popen
from time import sleep
from typing import Dict, Generator, List, Mapping, Optional, Self, Tuple

from tfmod.constants import (
    CONFIG_TFVARS,
    MODULE_TFVARS,
    MODULES_DIR,
    STATE_DIR,
    TERRAFORM_BIN,
)
from tfmod.error import TerraformError
from tfmod.io import logger
from tfmod.io.prompt import prompt_var
from tfmod.spec import Spec
from tfmod.terraform.value import dump_value, Value
from tfmod.terraform.variables import load_variables, Variable

PathLike = Path | str


# TODO: Wrap in an Error
def makedirs(path: PathLike) -> None:
    logger.debug(f"Creating directory {path}")
    os.makedirs(path, exist_ok=True)


# TODO: Wrap in an Error
def move(src: PathLike, dst: PathLike) -> None:
    try:
        shutil.move(src, dst)
    except FileNotFoundError as exc:
        logger.debug(f"Failure to move {src} to {dst}: {exc}")
    else:
        logger.info(f"Moved {src} to {dst}")


def clear_file(path: Path) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    logger.info(f"{path} cleared.")


class Terraform:
    def __init__(
        self,
        name: str,
        command: str = "apply",
        interval: float = 0.1,
        timeout: Optional[float] = None,
    ) -> None:
        self._name: str = name
        self._path: Path = MODULES_DIR / name
        self._workspace_path: Optional[Path] = None
        self._command: str = command
        self._interval: float = interval
        self._timeout: Optional[float] = timeout
        self._loaded_spec: bool = False
        self.__spec: Optional[Spec] = None
        self._env: Dict[str, str] = dict()
        self._vars: Dict[str, str] = dict()
        self._prompt_vars: Dict[str, Variable] = dict()
        self._var_files: List[str] = list()
        self._args: List[str] = list()

    def workspace(self, path=STATE_DIR / "workspace") -> Self:
        self._workspace_path = path
        return self

    def cleared(self) -> Self:
        clear_file(self._path / "terraform.tfstate")
        clear_file(self._path / "terraform.tfstate.backup")
        return self

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

    @property
    def _spec(self) -> Optional[Spec]:
        """
        The contents of the current spec.tfvars, if any
        """
        if not self._loaded_spec:
            self.__spec = Spec.load_optional()
            self._loaded_spec = True
        return self.__spec

    def spec(self) -> Self:
        """
        Load the current spec.tfvars
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

    @contextmanager
    def _workspace(self) -> Generator[None, None, None]:
        files = ["terraform.tfstate", "terraform.tfstate.backup"]
        workspace_path: Optional[Path] = None

        if self._workspace_path:
            workspace_path = self._workspace_path / os.getcwd()[1:] / self._name

        if workspace_path:
            logger.info(f"Loading workspace at {workspace_path}")
            makedirs(workspace_path)
            for file in files:
                move(workspace_path / file, self._path / file)

        yield

        if workspace_path:
            logger.info(f"Saving to workspace at {workspace_path}")
            for file in files:
                move(self._path / file, workspace_path)

    def _prompt(self) -> None:
        vars = load_variables(self._path)

        for name, var in self._prompt_vars.items():
            # Some variable names are postfixed with a _ because the
            # plain name is reserved in Terraform.
            name_in_spec = name[:-1] if name.endswith("_") else name

            description: Optional[str] = var.description
            default = var.default

            if name in vars and vars[name].description:
                description = vars[name].description
            if getattr(self._spec, name_in_spec, None) is not None:
                default = getattr(self._spec, name_in_spec)
            elif name in vars and vars[name].default:
                default = vars[name].default

            value = prompt_var(name, description=description, default=default)
            if value is not None:
                self._vars[name] = dump_value(value)

    def build(self) -> Tuple[List[str], Dict[str, str]]:
        """
        Build argv
        """

        self._prompt()

        args: List[str] = []
        args.append(f"-chdir={self._path}")
        args.append(self._command)

        for file in self._var_files:
            args.append(f"-var-file={file}")

        for name, value in self._vars.items():
            args.append("-var")
            args.append(f"{name}={value}")

        return args + self._args, self._env

    def _finish(self, exit_code: int) -> None:
        if exit_code:
            raise TerraformError(exit_code)

    def run(self, env: Mapping[str, str] = os.environ) -> None:
        """
        Run the Terraform command
        """
        with self._workspace():
            _args, _env = self.build()
            _env = dict(env, **_env)

            args = [TERRAFORM_BIN] + _args

            logger.info(f"Running Terraform with args: {_args}")

            with Popen(args, env=_env) as proc:
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
