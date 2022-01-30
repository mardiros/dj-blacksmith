from typing import Any, Dict

import pytest
from blacksmith import (
    SyncAbstractTransport,
    SyncClientFactory,
    SyncStaticDiscovery,
    HTTPRequest,
    HTTPResponse,
    HTTPTimeout,
)
from blacksmith.sd._sync.adapters.consul import _registry  # type: ignore

from django.test import override_settings
from dj_blacksmith.client._sync.client import (
    SyncDjBlacksmithClient,
    build_sd,
    client_factory,
)


class FakeConsulTransport(SyncAbstractTransport):
    def __call__(
        self, request: HTTPRequest, client_name: str, path: str, timeout: HTTPTimeout
    ) -> HTTPResponse:
        return HTTPResponse(
            200,
            {},
            [
                {
                    "ServiceAddress": f"{request.path['name']}",
                    "ServicePort": 80,
                }
            ],
        )


def consul_blacksmith_cli(url: str, tok: str) -> SyncClientFactory[Any, Any]:
    return SyncClientFactory(
        sd=SyncStaticDiscovery({("consul", "v1"): url}),
        registry=_registry,  # type: ignore
        transport=FakeConsulTransport(),
    )


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {
                "sd": "static",
                "static_sd_config": {
                    "srv": "http://srv:80",
                    "api/v1": "http://api.v1:80",
                },
            },
        },
        {
            "settings": {
                "sd": "router",
                "router_sd_config": {
                    "service_url_fmt": "http://{service}.{version}:80",
                    "unversioned_service_url_fmt": "http://{service}:80",
                },
            },
        },
        {
            "settings": {
                "sd": "consul",
                "consul_sd_config": {
                    "service_name_fmt": "{service}.{version}",
                    "service_url_fmt": "http://{address}:{port}",
                    "_client_factory": consul_blacksmith_cli,
                },
            },
        },
    ],
)
def test_build_sd(params: Dict[str, Any]):
    sd = build_sd(params["settings"])
    endpoint = sd.get_endpoint("srv", None)
    assert endpoint == "http://srv:80"

    endpoint = sd.get_endpoint("api", "v1")
    assert endpoint == "http://api.v1:80"


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {
                "default": {
                    "sd": "router",
                    "router_sd_config": {},
                    "proxies": {
                        "http://": "http://letmeout:8080/",
                        "https://": "https://letmeout:8443/",
                    },
                    "verify_certificate": False,
                    "timeout": {"read": 10, "connect": 5},
                }
            },
            "expected_proxies": {
                "http://": "http://letmeout:8080/",
                "https://": "https://letmeout:8443/",
            },
            "expected_verify_cert": False,
            "expected_timeout": HTTPTimeout(10, 5),
        },
        {
            "settings": {
                "default": {
                    "sd": "router",
                    "router_sd_config": {},
                }
            },
            "expected_proxies": None,
            "expected_verify_cert": True,
            "expected_timeout": HTTPTimeout(30, 15),
        },
    ],
)
def test_client_factory(params: Dict[str, Any], prometheus_registry: Any):
    with override_settings(BLACKSMITH_CLIENT=params["settings"]):
        cli = client_factory()
        assert cli.transport.proxies == params["expected_proxies"]
        assert cli.transport.verify_certificate == params["expected_verify_cert"]
        assert cli.timeout == params["expected_timeout"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {"default": {"sd": "router", "router_sd_config": {}}},
            "expected_proxies": None,
            "expected_verify_cert": True,
            "expected_timeout": HTTPTimeout(30, 15),
        },
    ],
)
def test_reuse_client_factory(
    params: Dict[str, Any], req: Any, prometheus_registry: Any
):
    with override_settings(BLACKSMITH_CLIENT=params["settings"]):
        dj_cli = SyncDjBlacksmithClient(req)
        cli = dj_cli()
        assert cli.transport.proxies == params["expected_proxies"]
        assert cli.transport.verify_certificate == params["expected_verify_cert"]
        assert cli.timeout == params["expected_timeout"]

        cli2 = dj_cli("default")
        assert cli is cli2
