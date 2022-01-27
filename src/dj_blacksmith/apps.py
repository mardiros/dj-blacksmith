from typing import Any
from blacksmith import scan
from django.apps import AppConfig
from django.conf import settings


def get_setting(name: str, default: Any= None) -> Any:
    return getattr(settings, f"BLACKSMITH_{name}", default)


class BlackmithConfig(AppConfig):
    name = "dj_blacksmith"
    verbose_name = "Blacksmith client"

    def ready(self):
        mods = get_setting("IMPORT", [])
        scan(*mods)
