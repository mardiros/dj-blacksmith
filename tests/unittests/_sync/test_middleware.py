from typing import Any, Dict

import pytest
from blacksmith import PrometheusMetrics
from prometheus_client import CollectorRegistry  # type: ignore

from dj_blacksmith.client._sync.middleware import SyncCircuitBreakerMiddlewareBuilder


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
    builder = SyncCircuitBreakerMiddlewareBuilder(params["settings"], params["metrics"])
    cbreaker = builder.build()
    assert (
        cbreaker.circuit_breaker.default_ttl == params["expected_ttl"]  # type: ignore
    )
    assert (
        cbreaker.circuit_breaker.default_threshold  # type: ignore
        == params["expected_threshold"]
    )
