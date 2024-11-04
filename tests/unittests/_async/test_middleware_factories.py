from typing import Any

import pytest
from django.test import RequestFactory

from dj_blacksmith.client._async.middleware_factory import (
    AsyncForwardHeaderFactoryBuilder,
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
def test_add_header(req: RequestFactory, params: dict[str, Any]):
    request = req.get("/", **params["req_headers"])
    fb = AsyncForwardHeaderFactoryBuilder({"forwarded_headers": params["fwd_headers"]})
    mid = fb(request)
    assert mid.headers == params["expected"]
