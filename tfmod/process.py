import os
import shlex
import subprocess
from typing import List, Literal, Mapping, Optional

from tfmod.io import logger

Direction = Literal["fetch"] | Literal["push"]


def run_out(argv: List[str], cwd: str = os.getcwd()) -> str:
    logger.start_quote(shlex.join(argv))

    proc = subprocess.run(argv, cwd=cwd, capture_output=True)
    proc.check_returncode()

    if proc.stderr:
        with logger.wrap_quote():
            print(proc.stderr.decode("unicode_escape"))
    # NOTE: This *may* not technically be safe to do, but here's hoping...
    return proc.stdout.decode("unicode_escape")


def run_test(argv: List[str], cwd: str = os.getcwd()) -> bool:
    logger.trace(f"Running: {shlex.join(argv)}")
    proc = subprocess.run(argv, cwd=cwd, capture_output=True)
    if proc.stderr:
        logger.trace(proc.stderr.decode("unicode_escape"))

    return proc.returncode == 0


def run_interactive(
    argv: List[str], cwd: str = os.getcwd(), env: Optional[Mapping[str, str]] = None
) -> None:
    with logger.quote(shlex.join(argv)):
        subprocess.run(argv, cwd=cwd, env=env, capture_output=False, check=True)
