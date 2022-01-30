import abc
from typing import Any, Mapping
from blacksmith import (
    AsyncHTTPMiddleware,
    AsyncCircuitBreakerMiddleware,
    PrometheusMetrics,
)


class AsyncHTTPMiddlewareBuilder(abc.ABC):
    def __init__(
        self,
        settings: Mapping[str, Any],
        metrics: PrometheusMetrics,
    ):
        self.settings = settings
        self.metrics = metrics

    @abc.abstractmethod
    def build(self) -> AsyncHTTPMiddleware:
        ...


class AsyncCircuitBreakerMiddlewareBuilder(AsyncHTTPMiddlewareBuilder):
    def build(self) -> AsyncHTTPMiddleware:
        return AsyncCircuitBreakerMiddleware(
            **self.settings.get("circuit_breaker", {}),
            metrics=self.metrics,
        )
