from typing import Any

import pytest

from dj_blacksmith._settings import get_clients, get_imports, get_setting


@pytest.mark.parametrize(
    "params",
    [
        {"setting": "IMPORT", "expected": ["testapp.resources"]},
        {"setting": "WHATEVER", "expected": None},
        {"setting": "default", "default": "foo", "expected": "foo"},
    ],
)
def test_get_setting(params: dict[str, Any]):
    setting = get_setting(params["setting"], params.get("default"))
    assert setting == params["expected"]


def test_get_imports():
    assert get_imports() == ["testapp.resources"]


def test_get_client():
    assert list(get_clients().keys()) == ["default", "alt_client"]
