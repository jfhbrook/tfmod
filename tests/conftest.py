# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Callable

import pytest
import tftest

from tfmod.constants import MODULES_DIR


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def tf_module() -> Callable[[str], tftest.TerraformTest]:
    def get_module(name: str) -> tftest.TerraformTest:
        tf = tftest.TerraformTest("spec", str(MODULES_DIR))
        tf.setup()
        return tf

    return get_module
