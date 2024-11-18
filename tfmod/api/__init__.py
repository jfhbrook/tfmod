# https://developer.hashicorp.com/terraform/registry/api-docs

from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    cast,
    Dict,
    Generator,
    List,
    Optional,
    Protocol,
    Set,
    TypeVar,
)

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
    next_offset: Optional[int] = None
    prev_offset: Optional[int] = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Meta":
        return cls(**data)


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

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Provider":
        return cls(**data)


@dataclass
class Resource:
    """
    A Terraform resource.
    """

    name: str
    type: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Resource":
        return cls(**data)


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

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Input":
        return cls(**data)


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

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ModuleInfo":
        return cls(
            **dict(data),
            inputs=[Input.from_json(input_) for input_ in data["inputs"]],
            provider_dependencies=[
                Provider.from_json(provider)
                for provider in data["provider_dependencies"]
            ],
            resources=[Resource.from_json(resource) for resource in data["resources"]],
        )


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

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ShortModule":
        return cls(**data)


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

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Module":
        return cls(
            **dict(
                data,
                root=ModuleInfo.from_json(data["root"]),
                submodules=[
                    ModuleInfo.from_json(module) for module in data["submodules"]
                ],
            )
        )


@dataclass
class ModuleList(Paginated):
    """
    A paginated list of Terraform modules.
    """

    meta: Meta
    modules: List[ShortModule]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ModuleList":
        return cls(
            meta=Meta.from_json(data["meta"]),
            modules=[ShortModule.from_json(module) for module in data["modules"]],
        )


@dataclass
class ShortRoot:
    """
    A short summary of a root module.
    """

    providers: List[Provider]
    dependencies: List[Dependency]
    deprecation: None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ShortRoot":
        return cls(
            **dict(
                data,
                providers=[
                    Provider.from_json(provider) for provider in data["providers"]
                ],
            )
        )


@dataclass
class ShortSubmodule:
    """
    A short summary of a submodule.
    """

    path: str
    providers: List[Provider]
    dependencies: List[Dependency]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ShortSubmodule":
        return cls(
            **dict(
                data,
                providers=[
                    Provider.from_json(provider) for provider in data["providers"]
                ],
            )
        )


@dataclass
class Version:
    """
    A module version.
    """

    version: str
    root: ShortRoot
    submodules: List[ShortSubmodule]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Version":
        return cls(
            **dict(
                data,
                root=ShortRoot.from_json(data["root"]),
                submodules=[
                    ShortSubmodule.from_json(submodule)
                    for submodule in data["submodules"]
                ],
            )
        )


@dataclass
class ModuleVersions:
    """
    Versions of a Terraform module.
    """

    source: str
    versions: List[Version]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ModuleVersions":
        return cls(
            **dict(
                data,
                versions=[Version.from_json(version) for version in data["versions"]],
            )
        )


@dataclass
class VersionList(Paginated):
    """
    A paginated list of versions of Terraform modules.
    """

    meta: Meta
    modules: List[ModuleVersions]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "VersionList":
        return cls(
            meta=Meta.from_json(data["meta"]),
            modules=[ModuleVersions.from_json(module) for module in data["modules"]],
        )


@dataclass
class Metrics:
    """
    Module metrics.
    """

    type: str
    id: str
    attributes: Dict[str, int]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Metrics":
        return cls(**data)


@dataclass
class Summary:
    """
    A metrics summary for a module.
    """

    data: Metrics

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Summary":
        return cls(data=Metrics.from_json(data["data"]))


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
    """
    An API client for the Terraform registry.
    """

    def __init__(
        self, base_url: str = "https://registry.terraform.io/v1/modules"
    ) -> None:
        self.base_url = base_url

    def list(
        self,
        namespace: Optional[str] = None,
        offset: Optional[int] = None,
        provider: Optional[str] = None,
        verified: bool = False,
    ) -> ModuleList:
        """
        List modules under a namespace.
        """

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
        """
        Search for modules.
        """

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
        """
        Get versions for a module given a provider.
        """

        url = f"{self.base_url}/{namespace}/{name}/{provider}/versions"

        res = requests.get(url)

        raise_for_status(res)

        data = res.json()

        return VersionList.from_json(data)

    def latest(
        self, namespace: str, name: str, offset: Optional[int] = None
    ) -> ModuleList:
        """
        Get the latest versions of a module.
        """

        url = f"{self.base_url}/{namespace}/{name}"

        params: Dict[str, str] = dict()

        if offset is not None:
            params["offset"] = str(offset)

        res = requests.get(url, params=params)

        raise_for_status(res)

        data = res.json()

        return ModuleList.from_json(data)

    def latest_for_provider(self, namespace: str, name: str, provider: str) -> Module:
        """
        Get the latest version of a module for a provider.
        """

        url = f"{self.base_url}/{namespace}/{name}/{provider}"

        res = requests.get(url)

        raise_for_status(res)

        data = res.json()

        return Module.from_json(data)

    def get(self, namespace: str, name: str, provider: str, version: str) -> Module:
        """
        Get a module for a specific provider and version.
        """

        url = f"{self.base_url}/{namespace}/{name}/{provider}/{version}"

        res = requests.get(url)

        raise_for_status(res)

        data = res.json()

        return Module.from_json(data)

    def _download(self, url: str) -> str:
        res = requests.get(url, allow_redirects=True)

        raise_for_status(res, {204})

        get: Optional[str] = res.headers["x-terraform-get"]

        if not get:
            raise ValueError("No download URL")

        return get

    def download_url(
        self, namespace: str, name: str, provider: str, version: str
    ) -> str:
        """
        Get the download URL for a specific version of a module.
        """
        url = f"{self.base_url}/{namespace}/{name}/{provider}/{version}/download"
        return self._download(url)

    def latest_download_url(self, namespace: str, name: str, provider: str):
        """
        Get the download URL for the latest version of a module.
        """

        url = f"{self.base_url}/{namespace}/{name}/{provider}/download"

        return self._download(url)

    def metrics(self, namespace: str, name: str, provider: str) -> Summary:
        """
        Get download metrics for a module and provider.
        """

        url = f"{self.base_url}/{namespace}/{name}/{provider}/downloads/summary"

        res = requests.get(url)

        raise_for_status(res)

        data = res.json()

        return Summary.from_json(data)


T = TypeVar("T", bound=Paginated)
Method = Callable[..., T]


def paginate(method: Method[T], *args: Any, **kwargs: Any) -> Generator[T, None, None]:
    """
    Iterate over a paginated method on APIClient.
    """

    res: T = method(*args, **kwargs)

    while res.meta.next_offset is not None:
        yield res
        res = method(*args, **dict(kwargs, offset=res.meta.next_offset))

    yield res
