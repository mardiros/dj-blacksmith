from typing import Any, Dict

import pytest
from blacksmith import (
    AsyncAbstractTransport,
    AsyncClientFactory,
    AsyncStaticDiscovery,
    HTTPRequest,
    HTTPResponse,
    HTTPTimeout,
)
from blacksmith.sd._async.adapters.consul import _registry  # type: ignore

from dj_blacksmith.client._async.client import build_sd


class FakeConsulTransport(AsyncAbstractTransport):
    async def __call__(
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


def consul_blacksmith_cli(url: str, tok: str) -> AsyncClientFactory[Any, Any]:
    return AsyncClientFactory(
        sd=AsyncStaticDiscovery({("consul", "v1"): url}),
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
async def test_build_sd(params: Dict[str, Any]):
    sd = build_sd(params["settings"])
    endpoint = await sd.get_endpoint("srv", None)
    assert endpoint == "http://srv:80"

    endpoint = await sd.get_endpoint("api", "v1")
    assert endpoint == "http://api.v1:80"
