# https://developer.hashicorp.com/terraform/registry/api-docs

from dataclasses import dataclass
from typing import Dict, List, Optional, Protocol, Set

import requests

# rate limit: 429
# load shedding: 503


class APIError(Exception):
    """
    A Terraform API error.
    """

    def __init__(self, code: int, errors: List[str]) -> None:
        self.code: int = code
        msg = "unspecified error"
        if len(errors) == 1:
            msg = errors[0]
        elif len(errors) > 1:
            msg = "errors from Terraform Registry API:\n" + "\n".join(
                [f"  - {error}" for error in errors]
            )
        super().__init__(msg)
        self.errors: List[str] = errors


@dataclass
class Meta:
    """
    Pagination metadata.
    """

    limit: int
    current_offset: int
    next_offset: Optional[int]
    prev_offset: Optional[int]


class Paginated(Protocol):
    """
    A paginated response.
    """

    meta: Meta


# I'm guessing at this, I haven't seen a module in the wild with dependencies
Dependency = str


@dataclass
class Provider:
    """
    A Terraform provider.
    """

    name: str
    namespace: str
    source: str
    version: str  # actually a version range


@dataclass
class Resource:
    """
    A Terraform resource.
    """

    name: str
    type: str


@dataclass
class Input:
    """
    An input to a Terraform module.
    """

    name: str
    type: str  # contains Terraform type
    description: str
    default: str  # contains Terraform value
    required: bool


@dataclass
class ModuleInfo:
    """
    Information about a Terraform root module or submodule.
    """

    path: str
    name: str
    readme: str
    empty: bool
    inputs: List[Input]
    dependencies: List[Dependency]
    provider_dependencies: List[Provider]
    resources: List[Resource]


@dataclass
class ShortModule:
    """
    A summary of a Terraform module.
    """

    id: str
    owner: str
    namespace: str
    name: str
    version: str
    provider: str
    provider_logo_url: str
    description: str
    source: str
    tag: str
    published_at: str  # TODO: parse as datetime.datetime
    downloads: int
    verified: bool


@dataclass
class Module:
    """
    A Terraform module.
    """

    id: str
    owner: str
    namespace: str
    name: str
    version: str
    provider: str
    provider_logo_url: str
    description: str
    source: str
    tag: str
    published_at: str  # TODO: parse as datetime.datetime
    downloads: int
    verified: bool
    root: ModuleInfo
    submodules: List[ModuleInfo]
    providers: List[str]
    versions: List[str]
    deprecation: None


@dataclass
class ModuleList(Paginated):
    """
    A paginated list of Terraform modules.
    """

    meta: Meta
    modules: List[ShortModule]


@dataclass
class ShortRoot:
    """
    A short summary of a root module.
    """

    providers: List[Provider]
    dependencies: List[Dependency]
    deprecation: None


@dataclass
class ShortSubmodule:
    """
    A short summary of a submodule.
    """

    path: str
    providers: List[Provider]
    dependencies: List[Dependency]


@dataclass
class Version:
    """
    A module version.
    """

    version: str
    root: ShortRoot
    submodules: List[ShortSubmodule]


@dataclass
class ModuleVersions:
    """
    Versions of a Terraform module.
    """

    source: str
    versions: List[Version]


@dataclass
class VersionList(Paginated):
    """
    A paginated list of versions of Terraform modules.
    """

    meta: Meta
    modules: List[ModuleVersions]


@dataclass
class Metrics:
    """
    Module metrics.
    """

    type: str
    id: str
    attributes: Dict[str, int]


@dataclass
class Summary:
    """
    A metrics summary for a module.
    """

    data: Metrics


def raise_for_status(res: requests.Response, codes: Optional[Set[int]] = None) -> None:
    if not codes:
        codes = {200}
    if res.status_code not in codes:
        try:
            json = res.json()
            errors = json["errors"]
            assert type(errors) == list
        except Exception as exc:
            raise APIError(res.status_code, []) from exc
        else:
            raise APIError(res.status_code, errors)


class APIClient:
    base_url = "https://registry.terraform.io/v1/modules"

    def list(
        self,
        namespace: Optional[str] = None,
        offset: Optional[int] = None,
        provider: Optional[str] = None,
        verified: bool = False,
    ) -> ModuleList:
        url = f"{self.base_url}/{namespace}" if namespace else self.base_url

        params: Dict[str, str] = dict()

        if offset is not None:
            params["offset"] = str(offset)
        if provider is not None:
            params["provider"] = provider
        if verified:
            params["verified"] = "true"
        res = requests.get(url, params=params)

        raise_for_status(res)

        data = res.json()

        return ModuleList(
            meta=Meta(**data["meta"]),
            modules=[ShortModule(**module) for module in data["modules"]],
        )

    def search(
        self,
        q: str,
        offset: Optional[int] = None,
        provider: Optional[str] = None,
        namespace: Optional[str] = None,
        verified: bool = False,
    ) -> ModuleList:
        url = f"{self.base_url}/search"

        params: Dict[str, str] = dict(q=q)

        if offset is not None:
            params["offset"] = str(offset)
        if provider is not None:
            params["provider"] = provider
        if namespace is not None:
            params["namespace"] = namespace
        if verified:
            params["verified"] = "true"

        res = requests.get(url, params=params)

        raise_for_status(res)

        data = res.json()

        return ModuleList(
            meta=Meta(**data["meta"]),
            modules=[ShortModule(**module) for module in data["modules"]],
        )

    def versions(self, namespace: str, name: str, provider: str) -> VersionList:
        url = f"{self.base_url}/{namespace}/{name}/{provider}/versions"

        res = requests.get(url)

        raise_for_status(res)

        data = res.json()

        return VersionList(
            meta=Meta(**data["meta"]),
            modules=[ModuleVersions(**module) for module in data["modules"]],
        )

    def _download(self, url: str) -> str:
        res = requests.get(url, allow_redirects=True)

        raise_for_status(res, {204})

        get: Optional[str] = res.headers["x-terraform-get"]

        if not get:
            raise ValueError("No download URL")

        return get

    def download(self, namespace: str, name: str, provider: str, version: str) -> str:
        url = f"{self.base_url}/{namespace}/{name}/{provider}/{version}/download"
        return self._download(url)

    def latest(
        self, namespace: str, name: str, offset: Optional[int] = None
    ) -> ModuleList:
        url = f"{self.base_url}/{namespace}/{name}"

        params: Dict[str, str] = dict()

        if offset is not None:
            params["offset"] = str(offset)

        res = requests.get(url, params=params)

        raise_for_status(res)

        data = res.json()

        return ModuleList(
            meta=Meta(**data["meta"]),
            modules=[ShortModule(**module) for module in data["modules"]],
        )

    def latest_for_provider(self, namespace: str, name: str, provider: str) -> Module:
        url = f"{self.base_url}/{namespace}/{name}/{provider}"

        res = requests.get(url)

        raise_for_status(res)

        data = res.json()

        return Module(
            **dict(
                data,
                root=ModuleInfo(
                    **dict(
                        data["root"],
                        inputs=[Input(**input_) for input_ in data["root"]["inputs"]],
                        provider_dependencies=[
                            Provider(**provider)
                            for provider in data["root"]["provider_dependencies"]
                        ],
                        resources=[
                            Resource(**resource)
                            for resource in data["root"]["resources"]
                        ],
                    )
                ),
                submodules=[
                    ModuleInfo(
                        **dict(
                            module,
                            inputs=[Input(**input_) for input_ in module["inputs"]],
                            provider_dependencies=[
                                Provider(**provider)
                                for provider in module["provider_dependencies"]
                            ],
                            resources=[
                                Resource(**resource) for resource in module["resources"]
                            ],
                        )
                    )
                    for module in data["submodules"]
                ],
            )
        )

    def get(self, namespace: str, name: str, provider: str, version: str) -> Module:
        url = f"{self.base_url}/{namespace}/{name}/{provider}/{version}"

        res = requests.get(url)

        raise_for_status(res)

        data = res.json()

        return Module(
            **dict(
                data,
                root=ModuleInfo(
                    **dict(
                        data["root"],
                        inputs=[Input(**input_) for input_ in data["root"]["inputs"]],
                        provider_dependencies=[
                            Provider(**provider)
                            for provider in data["root"]["provider_dependencies"]
                        ],
                        resources=[
                            Resource(**resource)
                            for resource in data["root"]["resources"]
                        ],
                    )
                ),
                submodules=[
                    ModuleInfo(
                        **dict(
                            module,
                            inputs=[Input(**input_) for input_ in module["inputs"]],
                            provider_dependencies=[
                                Provider(**provider)
                                for provider in module["provider_dependencies"]
                            ],
                            resources=[
                                Resource(**resource) for resource in module["resources"]
                            ],
                        )
                    )
                    for module in data["submodules"]
                ],
            )
        )

    def download_latest(self, namespace: str, name: str, provider: str):
        url = f"{self.base_url}/{namespace}/{name}/{provider}/download"

        return self._download(url)

    def metrics(self, namespace: str, name: str, provider: str) -> MetricsSummary:
        url = f"{self.base_url}/{namespace}/{name}/{provider}/downloads/summary"

        res = requests.get(url)

        raise_for_status(res)

        data = res.json()

        return Summary(data=Metrics(**data["data"]))
