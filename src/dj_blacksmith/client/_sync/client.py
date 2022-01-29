from typing import Any, Dict, Mapping, Optional, Tuple

from blacksmith import (
    HTTPTimeout,
    SyncAbstractServiceDiscovery,
    SyncClientFactory,
    SyncConsulDiscovery,
    SyncRouterDiscovery,
    SyncStaticDiscovery,
)
from django.http.request import HttpRequest

from dj_blacksmith._settings import get_clients


def build_sd(
    settings: Mapping[str, Mapping[str, Any]]
) -> SyncAbstractServiceDiscovery:
    sd_setting = settings.get("sd")
    if sd_setting == "consul":
        return SyncConsulDiscovery(**settings["consul_sd_config"])
    elif sd_setting == "router":
        return SyncRouterDiscovery(**settings["router_sd_config"])
    elif sd_setting == "static":
        endpoints: Dict[Tuple[str, Optional[str]], str] = {}
        for key, val in settings["static_sd_config"].items():
            if "/" in key:
                srv, ver = key.rsplit("/", 1)
            else:
                srv, ver = key, None
            endpoints[(srv, ver)] = val
        return SyncStaticDiscovery(endpoints)
    else:
        raise RuntimeError(f"Unkown service discovery {sd_setting}")


class SyncDjBlacksmith:
    def __init__(self, name: str = "default") -> None:
        settings = get_clients().get(name)
        if settings is None:
            raise RuntimeError(f"Client {name} does not exists")
        sd = build_sd(settings)
        timeout = settings.get("timeout", {})
        self.cli: SyncClientFactory[Any, Any] = SyncClientFactory(
            sd,
            proxies=settings.get("proxies"),
            verify_certificate=settings.get("verify_certificate", True),
            timeout=HTTPTimeout(**timeout),
        )

    def __call__(self, request: HttpRequest):
        ...
