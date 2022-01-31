"""Build Blacksmith middlewares from Django settings."""
import abc
from typing import Any, Mapping

from blacksmith import (
    PrometheusMetrics,
    SyncCircuitBreakerMiddleware,
    SyncHTTPMiddleware,
    SyncPrometheusMiddleware,
)


class SyncHTTPMiddlewareBuilder(abc.ABC):
    """Build middleware from settings."""

    def __init__(
        self,
        settings: Mapping[str, Any],
        metrics: PrometheusMetrics,
    ):
        self.settings = settings
        self.metrics = metrics

    @abc.abstractmethod
    def build(self) -> SyncHTTPMiddleware:
        """Build the middleware from the settings, optionnaly use the metrics."""


class SyncCircuitBreakerMiddlewareBuilder(SyncHTTPMiddlewareBuilder):
    """Build Circuit Breaker Middleware."""

    def build(self) -> SyncHTTPMiddleware:
        return SyncCircuitBreakerMiddleware(
            **self.settings.get("circuit_breaker", {}),
            metrics=self.metrics,
        )


class SyncPrometheusMiddlewareBuilder(SyncHTTPMiddlewareBuilder):
    """Build Prometheus Middleware."""

    def build(self) -> SyncPrometheusMiddleware:
        return SyncPrometheusMiddleware(metrics=self.metrics)
