from typing import Any, Dict

from .base import *  # noqa

INSTALLED_APPS.append("dj_blacksmith")  # noqa

BLACKSMITH_IMPORT = ["testapp.resources"]

BLACKSMITH_CLIENT: Dict[str, Any] = {
    "default": {
        "sd": "router",
        "router_sd_config": {},
    },
    "alt_client": {
        "sd": "static",
        "static_sd_config": {},
    },
}
