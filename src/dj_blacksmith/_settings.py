from typing import Any

from django.conf import settings


def get_setting(name: str, default: Any = None) -> Any:
    return getattr(settings, f"BLACKSMITH_{name}", default)


def get_imports() -> list[str]:
    return get_setting("IMPORT", [])


def get_clients() -> dict[str, Any]:
    return get_setting("CLIENT", {})


def get_transport() -> str:
    return get_setting("TRANSPORT")
