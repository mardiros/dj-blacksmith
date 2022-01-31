"""Build Blacksmith middlewares from Django settings."""
import abc
from typing import Any, Mapping

from blacksmith import (
    AsyncCircuitBreakerMiddleware,
    AsyncPrometheusMiddleware,
    AsyncHTTPMiddleware,
    PrometheusMetrics,
)


class AsyncHTTPMiddlewareBuilder(abc.ABC):
    """Build middleware from settings."""

    def __init__(
        self,
        settings: Mapping[str, Any],
        metrics: PrometheusMetrics,
    ):
        self.settings = settings
        self.metrics = metrics

    @abc.abstractmethod
    def build(self) -> AsyncHTTPMiddleware:
        """Build the middleware from the settings, optionnaly use the metrics."""


class AsyncCircuitBreakerMiddlewareBuilder(AsyncHTTPMiddlewareBuilder):
    """Build Circuit Breaker Middleware."""

    def build(self) -> AsyncHTTPMiddleware:
        return AsyncCircuitBreakerMiddleware(
            **self.settings.get("circuit_breaker", {}),
            metrics=self.metrics,
        )


class AsyncPrometheusMiddlewareBuilder(AsyncHTTPMiddlewareBuilder):
    """Build Prometheus Middleware."""

    def build(self) -> AsyncPrometheusMiddleware:
        return AsyncPrometheusMiddleware(metrics=self.metrics)
