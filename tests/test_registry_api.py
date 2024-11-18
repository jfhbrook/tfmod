# -*- coding: utf-8 -*-

import pytest


@pytest.mark.vcr
def test_list(api_client) -> None:
    modules = api_client.list()
