# type: ignore
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ["*"]
DEBUG = True
SECRET_KEY = "plokiploki"

INSTALLED_APPS = ["dj_blacksmith"]

MIDDLEWARE = []
ROOT_URLCONF = "notif.urls"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

BLACKSMITH_IMPORT = ["notif.resources"]

BLACKSMITH_CLIENT = {
    "default": {
        "sd": "consul",
        "consul_sd_config": {},
        "middlewares": [
            "dj_blacksmith.SyncPrometheusMiddlewareBuilder",
            "dj_blacksmith.SyncCircuitBreakerMiddlewareBuilder",
        ],
    },
}
