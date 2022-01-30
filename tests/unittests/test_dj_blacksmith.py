from typing import Any, Dict

from blacksmith import AsyncClientFactory
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


async def test_async_dj_blacksmith(req: Any):
    bmcli = AsyncDjBlacksmithClient(req.get("/"))
    cli = await bmcli()
    assert isinstance(cli, AsyncClientFactory)
