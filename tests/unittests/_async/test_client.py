from typing import Any, Dict

import pytest
from blacksmith.sd._async.adapters.consul import _registry  # type: ignore
from blacksmith.service._async.adapters.httpx import AsyncHttpxTransport
from django.test import override_settings
from prometheus_client import CollectorRegistry  # type: ignore

from blacksmith import (
    AsyncAbstractTransport,
    AsyncCircuitBreakerMiddleware,
    AsyncClientFactory,
    AsyncHTTPAddHeadersMiddleware,
    AsyncPrometheusMiddleware,
    AsyncStaticDiscovery,
    CollectionParser,
    HTTPRequest,
    HTTPResponse,
    HTTPTimeout,
    PrometheusMetrics,
)
from dj_blacksmith.client._async.client import (
    AsyncClientProxy,
    AsyncDjBlacksmithClient,
    build_collection_parser,
    build_metrics,
    build_middlewares,
    build_middlewares_factories,
    build_sd,
    build_transport,
    client_factory,
    middleware_factories,
)
from tests.unittests.fixtures import (
    AsyncDummyTransport,
    DummyCollectionParser,
    DummyMiddlewareFactory1,
    DummyMiddlewareFactory2,
)


class FakeConsulTransport(AsyncAbstractTransport):
    async def __call__(
        self, request: HTTPRequest, client_name: str, path: str, timeout: HTTPTimeout
    ) -> HTTPResponse:
        return HTTPResponse(
            200,
            {},
            [
                {
                    "Address": f"{request.path['name']}",
                    "ServiceAddress": f"{request.path['name']}",
                    "ServicePort": 80,
                }
            ],
        )


def consul_blacksmith_cli(url: str, tok: str) -> AsyncClientFactory[Any]:
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


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {"sd": "STATIC"},
            "expected_message": "Unkown service discovery STATIC",
        }
    ],
)
async def test_build_sd_errors(params: Dict[str, Any]):
    with pytest.raises(RuntimeError) as ctx:
        build_sd(params["settings"])
    assert str(ctx.value) == params["expected_message"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {},
            "expected": CollectionParser,
        },
        {
            "settings": {
                "collection_parser": "tests.unittests.fixtures.DummyCollectionParser",
            },
            "expected": DummyCollectionParser,
        },
    ],
)
def test_build_collection_parser(params: Dict[str, Any]):
    collection_parser = build_collection_parser(params["settings"])
    assert collection_parser is params["expected"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {},
            "expected": None,
        },
        {
            "settings": {
                "BLACKSMITH_TRANSPORT": "tests.unittests.fixtures.AsyncDummyTransport",
            },
            "expected": AsyncDummyTransport,
        },
    ],
)
def test_build_transport(params: Dict[str, Any]):
    with override_settings(**params["settings"]):
        transport = build_transport()
    assert transport is params["expected"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {},
            "expected_request_latency_seconds": [
                0.05,
                0.1,
                0.2,
                0.4,
                0.8,
                1.6,
                3.2,
                6.4,
                12.8,
                25.6,
            ],
            "expected_blacksmith_cache_latency_seconds": [
                0.005,
                0.01,
                0.02,
                0.04,
                0.08,
                0.16,
                0.32,
                0.64,
                1.28,
                2.56,
            ],
        },
        {
            "settings": {
                "metrics": {
                    "buckets": [0.1, 0.2],
                    "hit_cache_buckets": [0.01, 0.02],
                },
            },
            "expected_request_latency_seconds": [0.1, 0.2],
            "expected_blacksmith_cache_latency_seconds": [0.01, 0.02],
        },
    ],
)
def test_build_metrics(params: Dict[str, Any], prometheus_registry: CollectorRegistry):
    metrics = build_metrics(params["settings"])
    assert isinstance(metrics, PrometheusMetrics)
    assert (
        metrics.blacksmith_request_latency_seconds._kwargs["buckets"]  # type: ignore
        == params["expected_request_latency_seconds"]
    )

    assert (
        metrics.blacksmith_cache_latency_seconds._kwargs["buckets"]  # type: ignore
        == params["expected_blacksmith_cache_latency_seconds"]
    )


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {
                "middlewares": [
                    "dj_blacksmith.AsyncCircuitBreakerMiddlewareBuilder",
                    "dj_blacksmith.AsyncPrometheusMiddlewareBuilder",
                ]
            },
            "metrics": PrometheusMetrics(registry=CollectorRegistry()),
            "expected": [AsyncCircuitBreakerMiddleware, AsyncPrometheusMiddleware],
        },
    ],
)
async def test_build_middlewares(params: Dict[str, Any], prometheus_registry: Any):
    mdlws = build_middlewares(params["settings"], params["metrics"])
    assert [type(mdlw) for mdlw in mdlws] == params["expected"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {
                "BLACKSMITH_CLIENT": {
                    "default": {
                        "sd": "router",
                        "router_sd_config": {},
                        "proxies": {
                            "http://": "http://letmeout:8080/",
                            "https://": "https://letmeout:8443/",
                        },
                        "middlewares": [
                            "dj_blacksmith.AsyncCircuitBreakerMiddlewareBuilder",
                        ],
                        "verify_certificate": False,
                        "collection_parser": "tests.unittests.fixtures.DummyCollectionParser",  # noqa
                        "timeout": {"read": 10, "connect": 5},
                    },
                }
            },
            "expected_middlewares": [AsyncCircuitBreakerMiddleware],
            "expected_proxies": {
                "http://": "http://letmeout:8080/",
                "https://": "https://letmeout:8443/",
            },
            "expected_verify_cert": False,
            "expected_timeout": HTTPTimeout(10, 5),
            "expected_collection_parser": DummyCollectionParser,
            "expected_transport": AsyncHttpxTransport,
        },
        {
            "settings": {
                "BLACKSMITH_CLIENT": {
                    "default": {
                        "sd": "router",
                        "router_sd_config": {},
                    },
                },
                "BLACKSMITH_TRANSPORT": "tests.unittests.fixtures.AsyncDummyTransport",
            },
            "expected_middlewares": [],
            "expected_proxies": None,
            "expected_verify_cert": True,
            "expected_timeout": HTTPTimeout(30, 15),
            "expected_collection_parser": CollectionParser,
            "expected_transport": AsyncDummyTransport,
        },
        {
            "settings": {
                "BLACKSMITH_CLIENT": {
                    "default": {
                        "sd": "router",
                        "router_sd_config": {},
                    },
                },
            },
            "expected_middlewares": [],
            "expected_proxies": None,
            "expected_verify_cert": True,
            "expected_timeout": HTTPTimeout(30, 15),
            "expected_collection_parser": CollectionParser,
            "expected_transport": AsyncHttpxTransport,
        },
    ],
)
async def test_client_factory(params: Dict[str, Any], prometheus_registry: Any):
    with override_settings(**params["settings"]):
        cli = await client_factory()
        assert cli.transport.proxies == params["expected_proxies"]
        assert cli.transport.verify_certificate == params["expected_verify_cert"]
        assert cli.timeout == params["expected_timeout"]
        assert [type(m) for m in cli.middlewares] == params["expected_middlewares"]
        assert cli.collection_parser is params["expected_collection_parser"]
        assert isinstance(cli.transport, params["expected_transport"])


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {"default": {"sd": "router", "router_sd_config": {}}},
            "expected_message": "Client clicli does not exists",
        }
    ],
)
async def test_client_factory_errors(params: Dict[str, Any]):
    with pytest.raises(RuntimeError) as ctx:
        await client_factory("clicli")
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
async def test_reuse_client_factory(
    params: Dict[str, Any], req: Any, prometheus_registry: Any
):
    with override_settings(BLACKSMITH_CLIENT=params["settings"]):
        dj_cli = AsyncDjBlacksmithClient(req)
        cli = await dj_cli()
        factory = cli.client_factory
        assert factory.transport.proxies == params["expected_proxies"]
        assert factory.transport.verify_certificate == params["expected_verify_cert"]
        assert factory.timeout == params["expected_timeout"]

        cli2 = await dj_cli("default")
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


async def test_client_proxy_header_injection(
    dummy_async_client_factory: AsyncClientFactory[Any]
):
    prox = AsyncClientProxy(
        dummy_async_client_factory,
        [
            AsyncHTTPAddHeadersMiddleware(headers={"x-mdlwr-1": "1"}),
        ],
    )
    cli = await prox("dummy")
    resp = await cli.dummies.get({"name": "foo"})
    assert resp.raw_result.unwrap().headers == {"Foo": "Bar"}  # type: ignore
