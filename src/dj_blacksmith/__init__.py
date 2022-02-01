import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("dj_blacksmith").version
except pkg_resources.DistributionNotFound:
    # read the doc does not support poetry
    pass


from .client._async.client import AsyncDjBlacksmithClient
from .client._async.middleware import (
    AsyncCircuitBreakerMiddlewareBuilder,
    AsyncHTTPCacheMiddlewareBuilder,
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
    SyncPrometheusMiddlewareBuilder,
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
    # Middlewares Factory
    "AsyncAbstractMiddlewareFactoryBuilder",
    "AsyncForwardHeaderFactoryBuilder",
]
