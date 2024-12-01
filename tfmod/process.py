from dataclasses import dataclass
import os
import re
import shlex
import subprocess
from typing import Dict, List, Literal, Optional

from tfmod.constants import GIT_BIN
from tfmod.error import GitError
from tfmod.io import logger

Direction = Literal["fetch"] | Literal["push"]


def run_out(argv: List[str], cwd: str = os.getcwd()) -> str:
    proc = subprocess.run(argv, cwd=cwd, capture_output=True)
    proc.check_returncode()
    if proc.stderr:
        print(proc.stderr.decode("unicode_escape"))
    # NOTE: This *may* not technically be safe to do, but here's hoping...
    return proc.stdout.decode("unicode_escape")


def run_test(argv: List[str], cwd: str = os.getcwd()) -> bool:
    logger.trace(f"Running: {shlex.join(argv)}")
    proc = subprocess.run(argv, cwd=cwd, capture_output=True)
    if proc.stderr:
        logger.trace(proc.stderr.decode("unicode_escape"))

    return proc.returncode == 0


def run_interactive(argv: List[str], cwd: str = os.getcwd()) -> None:
    subprocess.run(argv, cwd=cwd, capture_output=False, check=True)
