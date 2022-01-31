from typing import Any, Dict

import pytest
from blacksmith import CacheControlPolicy, PrometheusMetrics
from prometheus_client import CollectorRegistry  # type: ignore

from dj_blacksmith.client._async.middleware import (
    AsyncCircuitBreakerMiddlewareBuilder,
    AsyncHTTPCacheMiddlewareBuilder,
    AsyncPrometheusMiddlewareBuilder,
)


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {},
            "metrics": PrometheusMetrics(registry=CollectorRegistry()),
            "expected_ttl": 30,
            "expected_threshold": 5,
        },
        {
            "settings": {
                "circuit_breaker": {
                    "threshold": 7,
                    "ttl": 42,
                }
            },
            "metrics": PrometheusMetrics(registry=CollectorRegistry()),
            "expected_ttl": 42,
            "expected_threshold": 7,
        },
    ],
)
def test_build_circuit_breaker(params: Dict[str, Any]):
    builder = AsyncCircuitBreakerMiddlewareBuilder(
        params["settings"], params["metrics"]
    )
    cbreaker = builder.build()
    assert (
        cbreaker.circuit_breaker.default_ttl == params["expected_ttl"]  # type: ignore
    )
    assert (
        cbreaker.circuit_breaker.default_threshold  # type: ignore
        == params["expected_threshold"]
    )


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {},
            "metrics": PrometheusMetrics(registry=CollectorRegistry()),
        },
    ],
)
def test_build_prometheus(params: Dict[str, Any]):
    builder = AsyncPrometheusMiddlewareBuilder(params["settings"], params["metrics"])
    prom = builder.build()
    assert prom.metrics == params["metrics"]


class DummyPolicy(CacheControlPolicy):
    pass


@pytest.mark.parametrize(
    "params",
    [
        {
            "settings": {"http_cache": {"redis": "redis://red/42"}},
            "metrics": PrometheusMetrics(registry=CollectorRegistry()),
            "expected_redis": {"db": 42, "host": "red"},
            "expected_policy": "CacheControlPolicy",
            "expected_serializer": "JsonSerializer",
        },
        {
            "settings": {
                "http_cache": {
                    "redis": "redis://red/42",
                    "policy": "tests.unittests.fixtures.DummyCachePolicy",
                    "serializer": "tests.unittests.fixtures.DummySerializer",
                }
            },
            "metrics": PrometheusMetrics(registry=CollectorRegistry()),
            "expected_redis": {"db": 42, "host": "red"},
            "expected_policy": "DummyCachePolicy",
            "expected_serializer": "DummySerializer",
        },
    ],
)
def test_build_cache(params: Dict[str, Any]):
    builder = AsyncHTTPCacheMiddlewareBuilder(params["settings"], params["metrics"])
    cache = builder.build()
    assert (
        cache._cache.connection_pool.connection_kwargs  # type: ignore
        == params["expected_redis"]
    )
    assert cache._policy.__class__.__name__ == params["expected_policy"]  # type: ignore
    assert (
        cache._serializer.__class__.__name__  # type: ignore
        == params["expected_serializer"]
    )
