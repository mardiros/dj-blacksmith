from typing import Any

from .base import *  # noqa

INSTALLED_APPS.append("dj_blacksmith")  # noqa

BLACKSMITH_IMPORT = ["testapp.resources"]

BLACKSMITH_CLIENT: dict[str, Any] = {
    "default": {
        "sd": "router",
        "router_sd_config": {},
    },
    "alt_client": {
        "sd": "static",
        "static_sd_config": {},
        "metrics": {
            "buckets": [0.5, 1, 3],
            "hit_cache_buckets": [0.1, 0.3, 1],
        },
        "middlewares": [
            "dj_blacksmith.AsyncCircuitBreakerMiddlewareBuilder",
        ],
        "forwarded_headers": ["Authorization", "Accept-Language"],
        "middleware_factories": [
            "dj_blacksmith.AsyncForwardHeaderFactoryBuilder",
        ],
    },
}
