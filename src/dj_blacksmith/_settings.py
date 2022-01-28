from typing import Any, Dict, List

from django.conf import settings


def get_setting(name: str, default: Any = None) -> Any:
    return getattr(settings, f"BLACKSMITH_{name}", default)


def get_imports() -> List[str]:
    return get_setting("IMPORT", [])


def get_clients() -> Dict[str, Any]:
    return get_setting("CLIENT", {})
