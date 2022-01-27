from typing import Any, Dict

import pytest
from dj_blacksmith.apps import get_setting
from blacksmith.domain.registry import registry
from blacksmith.domain.registry import ApiRoutes


@pytest.mark.parametrize(
    "params",
    [
        {"setting": "IMPORT", "expected": ["testapp.resources"]},
        {"setting": "WHATEVER", "expected": None},
        {"setting": "default", "default": "foo", "expected": "foo"},
    ],
)
def test_get_setting(params: Dict[str, Any]):
    setting = get_setting(params["setting"], params.get("default"))
    assert setting == params["expected"]


def test_import():
    clients: Dict[str, Any] = dict(registry.clients)  # type: ignore
    assert list(clients.keys()) == ["dummy"]
    assert list(clients["dummy"].keys()) == ["dummies"]
    dummies: ApiRoutes = clients["dummy"]["dummies"]
    assert dummies.resource is not None
    assert dummies.resource.path == "/dummies"

