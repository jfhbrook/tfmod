# -*- coding: utf-8 -*-

import pytest

from tfmod.api import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()
