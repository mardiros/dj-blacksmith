from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Type

from blacksmith import (
    AbstractCollectionParser,
    AsyncAbstractServiceDiscovery,
    AsyncClient,
    AsyncClientFactory,
    AsyncConsulDiscovery,
    AsyncHTTPMiddleware,
    AsyncRouterDiscovery,
    AsyncStaticDiscovery,
    HTTPTimeout,
    PrometheusMetrics,
)
from blacksmith.typing import ClientName
from django.http.request import HttpRequest
from django.utils.module_loading import import_string

from dj_blacksmith._settings import get_clients
from dj_blacksmith.client._async.middleware import AsyncHTTPMiddlewareBuilder
from dj_blacksmith.client._async.middleware_factory import (
    AsyncAbstractMiddlewareFactoryBuilder,
)


def build_sd(
    settings: Mapping[str, Mapping[str, Any]]
) -> AsyncAbstractServiceDiscovery:
    sd_setting = settings.get("sd")
    if sd_setting == "consul":
        return AsyncConsulDiscovery(**settings["consul_sd_config"])
    elif sd_setting == "router":
        return AsyncRouterDiscovery(**settings["router_sd_config"])
    elif sd_setting == "static":
        endpoints: Dict[Tuple[str, Optional[str]], str] = {}
        for key, val in settings["static_sd_config"].items():
            if "/" in key:
                srv, ver = key.rsplit("/", 1)
            else:
                srv, ver = key, None
            endpoints[(srv, ver)] = val
        return AsyncStaticDiscovery(endpoints)
    else:
        raise RuntimeError(f"Unkown service discovery {sd_setting}")


def build_collection_parser(settings: Dict[str, Any]) -> Type[AbstractCollectionParser]:
    cls = import_string(
        settings.get("collection_parser", "blacksmith.CollectionParser")
    )
    return cls


def build_middlewares(
    settings: Mapping[str, Any],
    metrics: PrometheusMetrics,
) -> Iterable[AsyncHTTPMiddleware]:
    middlewares: List[str] = settings.get("middlewares", [])
    for middleware in middlewares:
        cls: Type[AsyncHTTPMiddlewareBuilder] = import_string(middleware)
        yield cls(settings, metrics).build()


async def client_factory(name: str = "default") -> AsyncClientFactory[Any, Any]:
    settings = get_clients().get(name)
    if settings is None:
        raise RuntimeError(f"Client {name} does not exists")
    sd = build_sd(settings)
    timeout = settings.get("timeout", {})
    collection_parser = build_collection_parser(settings)
    cli: AsyncClientFactory[Any, Any] = AsyncClientFactory(
        sd,
        proxies=settings.get("proxies"),
        verify_certificate=settings.get("verify_certificate", True),
        timeout=HTTPTimeout(**timeout),
        collection_parser=collection_parser,
    )
    metrics = PrometheusMetrics()
    for middleware in build_middlewares(settings, metrics):
        cli.add_middleware(middleware)
    await cli.initialize()
    return cli


def build_middlewares_factories(
    settings: Mapping[str, Any],
) -> Iterable[AsyncAbstractMiddlewareFactoryBuilder]:
    middlewares: List[str] = settings.get("middleware_factories", [])
    for middleware in middlewares:
        cls: Type[AsyncAbstractMiddlewareFactoryBuilder] = import_string(middleware)
        yield cls(settings)


def middleware_factories(name: str = "default"):
    settings = get_clients()[name]
    return list(build_middlewares_factories(settings))


class AsyncClientProxy:
    def __init__(
        self,
        client_factory: AsyncClientFactory[Any, Any],
        middlewares: List[AsyncHTTPMiddleware],
    ):
        self.client_factory = client_factory
        self.middlewares = middlewares

    async def __call__(self, client_name: ClientName) -> AsyncClient[Any, Any]:
        cli = await self.client_factory(client_name)
        for middleware in self.middlewares:
            cli.add_middleware(middleware)
        return cli


class AsyncDjBlacksmithClient:
    client_factories: Dict[str, AsyncClientFactory[Any, Any]] = {}
    middleware_factories: Dict[str, List[AsyncAbstractMiddlewareFactoryBuilder]] = {}

    def __init__(self, request: HttpRequest):
        self.request = request

    async def __call__(self, factory_name: str = "default") -> AsyncClientProxy:

        if factory_name not in self.client_factories:
            self.client_factories[factory_name] = await client_factory(factory_name)
            self.middleware_factories[factory_name] = middleware_factories(factory_name)

        return AsyncClientProxy(
            self.client_factories[factory_name],
            [m(self.request) for m in self.middleware_factories[factory_name]],
        )
