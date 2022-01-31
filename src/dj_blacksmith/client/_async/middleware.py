"""Build Blacksmith middlewares from Django settings."""
import abc
from typing import Any, Mapping

import aioredis
from blacksmith import (
    AsyncCircuitBreakerMiddleware,
    AsyncHTTPAddHeadersMiddleware,
    AsyncHTTPBearerMiddleware,
    AsyncHTTPCacheMiddleware,
    AsyncHTTPMiddleware,
    AsyncPrometheusMiddleware,
    PrometheusMetrics,
)
from django.utils.module_loading import import_string


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


class AsyncHTTPCacheMiddlewareBuilder(AsyncHTTPMiddlewareBuilder):
    """Build HTTP Cache Middleware."""

    def build(self) -> AsyncHTTPCacheMiddleware:

        settings = self.settings["http_cache"]
        cache = aioredis.from_url(settings["redis"])  # type: ignore
        policy = import_string(settings.get("policy", "blacksmith.CacheControlPolicy"))
        srlz = import_string(settings.get("serializer", "blacksmith.JsonSerializer"))
        return AsyncHTTPCacheMiddleware(
            cache=cache,  # type: ignore
            policy=policy(),
            metrics=self.metrics,
            serializer=srlz(),
        )


class AsyncHTTPAddHeadersMiddlewareBuilder(AsyncHTTPMiddlewareBuilder):
    """Add header."""

    def build(self) -> AsyncHTTPAddHeadersMiddleware:
        headers = self.settings["http_headers"]
        return AsyncHTTPAddHeadersMiddleware(headers)


class AsyncHTTPBearerMiddlewareBuilder(AsyncHTTPMiddlewareBuilder):
    """Add header."""

    def build(self) -> AsyncHTTPBearerMiddleware:
        headers = self.settings["bearer_token"]
        return AsyncHTTPBearerMiddleware(headers)
