import abc
from typing import Any, Mapping

from blacksmith import (
    PrometheusMetrics,
    SyncCircuitBreakerMiddleware,
    SyncHTTPMiddleware,
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
    """Build Circuit Breaker middleware."""

    def build(self) -> SyncHTTPMiddleware:
        return SyncCircuitBreakerMiddleware(
            **self.settings.get("circuit_breaker", {}),
            metrics=self.metrics,
        )
