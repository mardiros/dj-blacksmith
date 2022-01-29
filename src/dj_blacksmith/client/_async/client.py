from typing import Any, Dict, Mapping, Optional, Tuple
from blacksmith import (
    AsyncClientFactory,
    AsyncConsulDiscovery,
    AsyncRouterDiscovery,
    AsyncAbstractServiceDiscovery,
    AsyncStaticDiscovery,
)
from django.http.request import HttpRequest


from dj_blacksmith._settings import get_clients


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


class AsyncDjBlacksmith:
    def __init__(self, name: str = "default") -> None:
        settings = get_clients().get(name)
        if settings is None:
            raise RuntimeError(f"Client {name} does not exists")
        sd = build_sd(settings)
        self.cli: AsyncClientFactory[Any, Any] = AsyncClientFactory(
            sd,
            proxies=settings.get("proxies"),
            verify_certificate=settings.get("verify_certificate", True),
        )

    def __call__(self, request: HttpRequest):
        ...
