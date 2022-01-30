from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Type
from blacksmith import (
    AsyncClientFactory,
    AsyncConsulDiscovery,
    AsyncHTTPMiddleware,
    AsyncRouterDiscovery,
    AsyncAbstractServiceDiscovery,
    AsyncStaticDiscovery,
    HTTPTimeout,
    PrometheusMetrics,
)
from blacksmith.typing import ClientName
from django.http.request import HttpRequest
from django.utils.module_loading import import_string


from dj_blacksmith._settings import get_clients
from dj_blacksmith.client._async.middleware import AsyncHTTPMiddlewareBuilder


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


def build_middlewares(
    metrics: PrometheusMetrics,
    settings: Mapping[str, Any]
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
    cli: AsyncClientFactory[Any, Any] = AsyncClientFactory(
        sd,
        proxies=settings.get("proxies"),
        verify_certificate=settings.get("verify_certificate", True),
        timeout=HTTPTimeout(**timeout),
    )
    metrics = PrometheusMetrics()
    for middleware in build_middlewares(metrics, settings):
        cli.add_middleware(middleware)
    await cli.initialize()
    return cli


class AsyncDjBlacksmithClient:
    clients: Dict[str, AsyncClientFactory[Any, Any]] = {}

    def __init__(self, request: HttpRequest):
        self.request = request

    async def __call__(
        self, client_name: ClientName = "default"
    ) -> AsyncClientFactory[Any, Any]:

        if client_name not in self.clients:
            self.clients[client_name] = await client_factory(client_name)

        return self.clients[client_name]
