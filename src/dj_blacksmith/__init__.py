from importlib import metadata

__version__ = metadata.version("dj_blacksmith")


from .client._async.client import AsyncDjBlacksmithClient
from .client._async.middleware import (
    AsyncCircuitBreakerMiddlewareBuilder,
    AsyncHTTPCacheMiddlewareBuilder,
    AsyncLoggingMiddlewareBuilder,
    AsyncPrometheusMiddlewareBuilder,
)
from .client._async.middleware_factory import (
    AsyncAbstractMiddlewareFactoryBuilder,
    AsyncForwardHeaderFactoryBuilder,
)
from .client._sync.client import SyncDjBlacksmithClient
from .client._sync.middleware import (
    SyncCircuitBreakerMiddlewareBuilder,
    SyncHTTPCacheMiddlewareBuilder,
    SyncLoggingMiddlewareBuilder,
    SyncPrometheusMiddlewareBuilder,
)
from .client._sync.middleware_factory import (
    SyncAbstractMiddlewareFactoryBuilder,
    SyncForwardHeaderFactoryBuilder,
)

__all__ = [
    # Clients
    "AsyncDjBlacksmithClient",
    "SyncDjBlacksmithClient",
    # Middlewares
    "AsyncCircuitBreakerMiddlewareBuilder",
    "SyncCircuitBreakerMiddlewareBuilder",
    "AsyncPrometheusMiddlewareBuilder",
    "SyncPrometheusMiddlewareBuilder",
    "AsyncHTTPCacheMiddlewareBuilder",
    "SyncHTTPCacheMiddlewareBuilder",
    "AsyncLoggingMiddlewareBuilder",
    "SyncLoggingMiddlewareBuilder",
    # Middlewares Factory
    "AsyncAbstractMiddlewareFactoryBuilder",
    "AsyncForwardHeaderFactoryBuilder",
    "SyncAbstractMiddlewareFactoryBuilder",
    "SyncForwardHeaderFactoryBuilder",
]
