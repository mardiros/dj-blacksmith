from typing import Any, Dict

import pytest
from blacksmith import (
    SyncAbstractTransport,
    SyncCircuitBreakerMiddleware,
    SyncClientFactory,
    SyncHTTPAddHeadersMiddleware,
    SyncPrometheusMiddleware,
    SyncStaticDiscovery,
    HTTPRequest,
    HTTPResponse,
    HTTPTimeout,
    PrometheusMetrics,
)
from blacksmith.sd._sync.adapters.consul import _registry  # type: ignore
from django.test import override_settings
from prometheus_client import CollectorRegistry  # type: ignore

from dj_blacksmith.client._sync.client import (
    SyncClientProxy,
    SyncDjBlacksmithClient,
    build_middlewares,
    build_middlewares_factories,
    build_sd,
    client_factory,
    middleware_factories,
)
from tests.unittests.fixtures import DummyMiddlewareFactory1, DummyMiddlewareFactory2


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
            "settings": {"sd": "STATIC"},
            "expected_message": "Unkown service discovery STATIC",
        }
    ],
)
def test_build_sd_errors(params: Dict[str, Any]):
    with pytest.raises(RuntimeError) as ctx:
        build_sd(params["settings"])
    assert str(ctx.value) == params["expected_message"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {
                "middlewares": [
                    "dj_blacksmith.SyncCircuitBreakerMiddlewareBuilder",
                    "dj_blacksmith.SyncPrometheusMiddlewareBuilder",
                ]
            },
            "metrics": PrometheusMetrics(registry=CollectorRegistry()),
            "expected": [SyncCircuitBreakerMiddleware, SyncPrometheusMiddleware],
        },
    ],
)
def test_build_middlewares(params: Dict[str, Any], prometheus_registry: Any):
    mdlws = build_middlewares(params["settings"], params["metrics"])
    assert [type(mdlw) for mdlw in mdlws] == params["expected"]


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
                    "middlewares": [
                        "dj_blacksmith.SyncCircuitBreakerMiddlewareBuilder",
                    ],
                    "verify_certificate": False,
                    "timeout": {"read": 10, "connect": 5},
                }
            },
            "expected_middlewares": [SyncCircuitBreakerMiddleware],
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
            "expected_middlewares": [],
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
        assert [type(m) for m in cli.middlewares] == params["expected_middlewares"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {"default": {"sd": "router", "router_sd_config": {}}},
            "expected_message": "Client clicli does not exists",
        }
    ],
)
def test_client_factory_errors(params: Dict[str, Any]):
    with pytest.raises(RuntimeError) as ctx:
        client_factory("clicli")
    assert str(ctx.value) == params["expected_message"]


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
        factory = cli.client_factory
        assert factory.transport.proxies == params["expected_proxies"]
        assert factory.transport.verify_certificate == params["expected_verify_cert"]
        assert factory.timeout == params["expected_timeout"]

        cli2 = dj_cli("default")
        assert cli.client_factory is cli2.client_factory


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {
                "middleware_factories": [
                    "tests.unittests.fixtures.DummyMiddlewareFactory1",
                    "tests.unittests.fixtures.DummyMiddlewareFactory2",
                ]
            }
        }
    ],
)
def test_build_middlewares_factories(params: Dict[str, Any]):
    factories = list(build_middlewares_factories(params["settings"]))
    assert factories == [DummyMiddlewareFactory1({}), DummyMiddlewareFactory2({})]


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {
                "default": {
                    "middleware_factories": [
                        "tests.unittests.fixtures.DummyMiddlewareFactory1",
                        "tests.unittests.fixtures.DummyMiddlewareFactory2",
                    ]
                }
            }
        }
    ],
)
def test_middleware_factories(params: Dict[str, Any]):
    with override_settings(BLACKSMITH_CLIENT=params["settings"]):
        factories = middleware_factories()
    assert factories == [DummyMiddlewareFactory1({}), DummyMiddlewareFactory2({})]


def test_client_proxy_header_injection(
    dummy_sync_client_factory: SyncClientFactory[Any, Any]
):
    prox = SyncClientProxy(
        dummy_sync_client_factory,
        [
            SyncHTTPAddHeadersMiddleware(headers={"x-mdlwr-1": "1"}),
        ],
    )
    cli = prox("dummy")
    resp = cli.dummies.get({"name": "foo"})
    assert resp.http_response.headers == {"Foo": "Bar"}  # type: ignore
