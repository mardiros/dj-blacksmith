"""Build Blacksmith middlewares from Django settings."""
import abc
from typing import Any, Mapping

import aioredis
from blacksmith import (
    PrometheusMetrics,
    SyncCircuitBreakerMiddleware,
    SyncHTTPAddHeadersMiddleware,
    SyncHTTPBearerMiddleware,
    SyncHTTPCacheMiddleware,
    SyncHTTPMiddleware,
    SyncPrometheusMiddleware,
)
from django.utils.module_loading import import_string


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


class SyncHTTPCacheMiddlewareBuilder(SyncHTTPMiddlewareBuilder):
    """Build HTTP Cache Middleware."""

    def build(self) -> SyncHTTPCacheMiddleware:

        settings = self.settings["http_cache"]
        cache = aioredis.from_url(settings["redis"])  # type: ignore
        policy = import_string(settings.get("policy", "blacksmith.CacheControlPolicy"))
        srlz = import_string(settings.get("serializer", "blacksmith.JsonSerializer"))
        return SyncHTTPCacheMiddleware(
            cache=cache,  # type: ignore
            policy=policy(),
            metrics=self.metrics,
            serializer=srlz(),
        )


class SyncHTTPAddHeadersMiddlewareBuilder(SyncHTTPMiddlewareBuilder):
    """Add header."""

    def build(self) -> SyncHTTPAddHeadersMiddleware:
        headers = self.settings["http_headers"]
        return SyncHTTPAddHeadersMiddleware(headers)


class SyncHTTPBearerMiddlewareBuilder(SyncHTTPMiddlewareBuilder):
    """Add header."""

    def build(self) -> SyncHTTPBearerMiddleware:
        headers = self.settings["bearer_token"]
        return SyncHTTPBearerMiddleware(headers)
