# https://developer.hashicorp.com/terraform/registry/api-docs

from dataclasses import dataclass
import datetime
from typing import Any, Dict, List, Optional, Protocol, Set, Type

import requests


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


class RateLimitError(APIError):
    """
    A rate limit error.
    """

    pass


class LoadSheddingError(APIError):
    """
    An error raised when the registry is load shedding.
    """

    pass


def as_[T](x: Any, type_: Type[T]) -> T:
    if type(x) != type_:
        raise ValueError(f"{x} is not a {type_}")
    return x


def as_optional[T](x: Any, type_: Type[T]) -> Optional[T]:
    if x is None:
        return x
    if type(x) != type_:
        raise ValueError(f"{x} is not a {type_}")
    return x


def as_list[T](x: Any, type_: Type[T]) -> List[T]:
    xs = as_(x, list)
    return [as_(x, type_) for x in xs]


def as_none(x: Any) -> None:
    if x is not None:
        raise ValueError(f"{x} is not None")
    return x


def as_datetime(x: Any) -> datetime.datetime:
    s = as_(x, str)
    return datetime.datetime.fromisoformat(s)


@dataclass
class Meta:
    """
    Pagination metadata.
    """

    limit: int
    current_offset: int
    next_offset: Optional[int] = None
    prev_offset: Optional[int] = None
    next_url: Optional[str] = None

    @classmethod
    def from_json(cls, data: Optional[Dict[str, Any]]) -> "Optional[Meta]":
        if data is None:
            return None
        return cls(
            **dict(
                data,
                limit=as_(data["limit"], int),
                current_offset=as_(data["current_offset"], int),
                next_offset=as_optional(data.get("next_offset", None), int),
                prev_offset=as_optional(data.get("prev_offset", None), int),
                next_url=as_optional(data.get("next_url", None), str),
            )
        )


class Paginated(Protocol):
    """
    A paginated response.
    """

    meta: Optional[Meta]


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
        return cls(
            **dict(
                data,
                name=as_(data["name"], str),
                namespace=as_(data["namespace"], str),
                source=as_(data["source"], str),
                version=as_(data["version"], str),
            )
        )


@dataclass
class Resource:
    """
    A Terraform resource.
    """

    name: str
    type: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Resource":
        return cls(
            **dict(
                data,
                name=as_(data["name"], str),
                type=as_(data["type"], str),
            )
        )


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
        return cls(
            **dict(
                data,
                name=as_(data["name"], str),
                type=as_(data["type"], str),
                description=as_(data["description"], str),
                required=as_(data["required"], bool),
            )
        )


@dataclass
class Output:
    """
    An output from a Terraform module.
    """

    name: str
    description: str

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Output":
        return cls(
            **dict(
                data,
                name=as_(data["name"], str),
                description=as_(data["description"], str),
            )
        )


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
    outputs: List[Output]
    dependencies: List[Dependency]
    provider_dependencies: List[Provider]
    resources: List[Resource]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ModuleInfo":
        return cls(
            **dict(
                data,
                path=as_(data["path"], str),
                name=as_(data["name"], str),
                readme=as_(data["readme"], str),
                empty=as_(data["empty"], bool),
                inputs=[Input.from_json(input_) for input_ in data["inputs"]],
                outputs=[Output.from_json(output) for output in data["outputs"]],
                provider_dependencies=[
                    Provider.from_json(provider)
                    for provider in data["provider_dependencies"]
                ],
                resources=[
                    Resource.from_json(resource) for resource in data["resources"]
                ],
            )
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
    published_at: datetime.datetime
    downloads: int
    verified: bool

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ShortModule":
        return cls(
            **dict(
                data,
                id=as_(data["id"], str),
                owner=as_(data["owner"], str),
                namespace=as_(data["namespace"], str),
                name=as_(data["name"], str),
                version=as_(data["version"], str),
                provider=as_(data["provider"], str),
                provider_logo_url=as_(data["provider_logo_url"], str),
                description=as_(data["description"], str),
                source=as_(data["source"], str),
                tag=as_(data["tag"], str),
                published_at=as_datetime(data["published_at"]),
                downloads=as_(data["downloads"], int),
                verified=as_(data["verified"], bool),
            )
        )


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
    published_at: datetime.datetime
    downloads: int
    verified: bool
    root: ModuleInfo
    submodules: List[ModuleInfo]
    examples: List[ModuleInfo]
    providers: List[str]
    versions: List[str]
    deprecation: None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Module":
        return cls(
            **dict(
                data,
                id=as_(data["id"], str),
                owner=as_(data["owner"], str),
                namespace=as_(data["namespace"], str),
                name=as_(data["name"], str),
                version=as_(data["version"], str),
                provider=as_(data["provider"], str),
                provider_logo_url=as_(data["provider_logo_url"], str),
                description=as_(data["description"], str),
                source=as_(data["source"], str),
                tag=as_(data["tag"], str),
                published_at=as_datetime(data["published_at"]),
                downloads=as_(data["downloads"], int),
                verified=as_(data["verified"], bool),
                root=ModuleInfo.from_json(data["root"]),
                submodules=[
                    ModuleInfo.from_json(module) for module in data["submodules"]
                ],
                examples=[
                    ModuleInfo.from_json(example) for example in data["examples"]
                ],
                providers=as_list(data["providers"], str),
                versions=as_list(data["versions"], str),
                deprecation=as_none(data["deprecation"]),
            )
        )


@dataclass
class ModuleList(Paginated):
    """
    A paginated list of Terraform modules.
    """

    meta: Optional[Meta]
    modules: List[ShortModule]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ModuleList":
        return cls(
            meta=Meta.from_json(data.get("meta", None)),
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
                dependencies=as_list(data["dependencies"], Dependency),
                deprecation=as_none(data.get("deprecation", None)),
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
                dependencies=as_list(data["dependencies"], Dependency),
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
    deprecation: None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Version":
        return cls(
            **dict(
                data,
                version=as_(data["version"], str),
                root=ShortRoot.from_json(data["root"]),
                submodules=[
                    ShortSubmodule.from_json(submodule)
                    for submodule in data["submodules"]
                ],
                deprecation=as_none(data["deprecation"]),
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
                source=as_(data["source"], str),
                versions=[Version.from_json(version) for version in data["versions"]],
            )
        )


@dataclass
class VersionList(Paginated):
    """
    A paginated list of versions of Terraform modules.
    """

    meta: Optional[Meta]
    modules: List[ModuleVersions]

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "VersionList":
        return cls(
            meta=Meta.from_json(data.get("meta", None)),
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
        return cls(
            **dict(
                data,
                type=as_(data["type"], str),
                id=as_(data["id"], str),
                attributes=as_(data["attributes"], dict),
            )
        )


@dataclass
class Summary:
    """
    A metrics summary for a module.
    """

    data: Metrics

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Summary":
        return cls(data=Metrics.from_json(data["data"]))


def raise_for_status(
    res: requests.Response, success_codes: Optional[Set[int]] = None
) -> None:
    if not success_codes:
        success_codes = {200}
    if res.status_code not in success_codes:
        cls = APIError
        if res.status_code == 429:
            cls = RateLimitError
        elif res.status_code == 503:
            cls = LoadSheddingError
        try:
            json = res.json()
            errors = json["errors"]
            assert type(errors) == list
        except Exception as exc:
            raise cls(res.status_code, []) from exc
        else:
            raise cls(res.status_code, errors)


class APIClient:
    """
    An API client for the Terraform registry.
    """

    def __init__(self, base_url: str = "https://registry.terraform.io") -> None:
        self.base_url = f"{base_url}/v1/modules"
        self.v2_base_url = f"{base_url}/v2/modules"

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

        print(url)

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

        url = f"{self.v2_base_url}/{namespace}/{name}/{provider}/downloads/summary"

        res = requests.get(url)

        raise_for_status(res)

        data = res.json()

        return Summary.from_json(data)
