import pytest
from typing import Any, Dict

from blacksmith import AsyncCircuitBreakerMiddleware, AsyncClientFactory
from blacksmith.domain.registry import ApiRoutes, registry

from dj_blacksmith.client._async.client import AsyncDjBlacksmithClient


def test_import():
    # test that the app testapp has loaded its resource while ready

    clients: Dict[str, Any] = dict(registry.clients)  # type: ignore
    assert list(clients.keys()) == ["dummy"]
    assert list(clients["dummy"].keys()) == ["dummies"]
    dummies: ApiRoutes = clients["dummy"]["dummies"]
    assert dummies.resource is not None
    assert dummies.resource.path == "/dummies"


@pytest.mark.parametrize(
    "params",
    [
        {
            "client": "default",
            "middlewares": [],
        },
        {
            "client": "alt_client",
            "middlewares": [AsyncCircuitBreakerMiddleware],
        },
    ],
)
async def test_async_dj_blacksmith(
    params: Dict[str, Any], req: Any, prometheus_registry: Any
):
    bmcli = AsyncDjBlacksmithClient(req.get("/"))
    cli = await bmcli(params["client"])
    assert isinstance(cli, AsyncClientFactory)
    assert [type(mid) for mid in cli.middlewares] == params["middlewares"]
