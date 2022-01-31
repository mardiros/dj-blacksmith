import abc
from typing import Any, Mapping

from blacksmith import (
    AsyncCircuitBreakerMiddleware,
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
    """Build Circuit Breaker middleware."""

    def build(self) -> AsyncHTTPMiddleware:
        return AsyncCircuitBreakerMiddleware(
            **self.settings.get("circuit_breaker", {}),
            metrics=self.metrics,
        )
