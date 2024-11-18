# -*- coding: utf-8 -*-

import pytest

from tfmod.api import (
    Input,
    Meta,
    Metrics,
    Module,
    ModuleInfo,
    ModuleList,
    ModuleVersions,
    Output,
    Provider,
    Resource,
    ShortModule,
    ShortRoot,
    ShortSubmodule,
    Summary,
    Version,
    VersionList,
)


@pytest.mark.vcr
def test_list(api_client, snapshot) -> None:
    modules = api_client.list()

    assert modules == snapshot


@pytest.mark.vcr
def test_list_namespace(api_client, snapshot) -> None:
    modules = api_client.list("terraform-aws-modules")

    assert modules == snapshot


@pytest.mark.vcr
def test_search(api_client) -> None:
    modules = api_client.search("dokku")

    assert modules == ModuleList(
        meta=Meta(
            limit=15,
            current_offset=0,
            next_offset=None,
            prev_offset=None,
        ),
        modules=[],
    )


@pytest.mark.vcr
def test_versions(api_client, snapshot) -> None:
    versions = api_client.versions("terraform-alicloud-modules", "disk", "alicloud")

    assert versions == snapshot


@pytest.mark.vcr
def test_latest(api_client, snapshot) -> None:
    modules = api_client.latest("hashicorp", "consul")

    assert modules == snapshot


@pytest.mark.vcr
def test_latest_for_provider(api_client, snapshot) -> None:
    module = api_client.latest_for_provider("hashicorp", "consul", "aws")

    assert module == snapshot


@pytest.mark.vcr
def test_get(api_client, snapshot) -> None:
    module = api_client.get("hashicorp", "consul", "aws", "0.11.0")

    assert module == snapshot


@pytest.mark.vcr
def test_download_url(api_client) -> None:
    url = api_client.download_url("hashicorp", "consul", "aws", "0.11.0")

    assert (
        url
        == "git::https://github.com/hashicorp/terraform-aws-consul?ref=e9ceb573687c3d28516c9e3714caca84db64a766"
    )


@pytest.mark.vcr
def test_latest_download_url(api_client) -> None:
    url = api_client.latest_download_url("hashicorp", "consul", "aws")

    assert (
        url
        == "git::https://github.com/hashicorp/terraform-aws-consul?ref=e9ceb573687c3d28516c9e3714caca84db64a766"
    )


@pytest.mark.vcr
def test_metrics(api_client) -> None:
    metrics = api_client.metrics("hashicorp", "consul", "aws")

    assert metrics == Summary(
        data=Metrics(
            type="module-downloads-summary",
            id="hashicorp/consul/aws",
            attributes={"month": 967, "total": 185417, "week": 513, "year": 44981},
        )
    )
