from typing import Any, Dict

import pytest
from django.test import RequestFactory

from dj_blacksmith.client._sync.middleware_factory import (
    SyncForwardHeaderFactoryBuilder,
)


@pytest.mark.parametrize(
    "params",
    [
        {
            "req_headers": {"HTTP_AUTHORIZATION": "Bearer abc"},
            "fwd_headers": ["Authorization"],
            "expected": {"Authorization": "Bearer abc"},
        }
    ],
)
def test_add_header(req: RequestFactory, params: Dict[str, Any]):
    request = req.get("/", **params["req_headers"])
    fb = SyncForwardHeaderFactoryBuilder({"forwarded_headers": params["fwd_headers"]})
    mid = fb(request)
    assert mid.headers == params["expected"]
