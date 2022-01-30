import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("dj_blacksmith").version
except pkg_resources.DistributionNotFound:
    # read the doc does not support poetry
    pass


from .client._async.middleware import AsyncCircuitBreakerMiddlewareBuilder


__all__ = ["AsyncCircuitBreakerMiddlewareBuilder"]
