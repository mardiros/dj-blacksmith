from typing import Any

import prometheus_client  # type: ignore
import pytest
from django.test import RequestFactory

from blacksmith import (
    AsyncAbstractTransport,
    AsyncClientFactory,
    AsyncRouterDiscovery,
    HTTPRequest,
    HTTPResponse,
    HTTPTimeout,
    SyncAbstractTransport,
    SyncClientFactory,
    SyncRouterDiscovery,
)


@pytest.fixture
def req():
    return RequestFactory()


@pytest.fixture
def prometheus_registry():
    prometheus_client.REGISTRY = prometheus_client.CollectorRegistry()
    yield prometheus_client.REGISTRY


class AsyncDummyTransport(AsyncAbstractTransport):
    async def __call__(
        self,
        req: HTTPRequest,
        client_name: str,
        path: str,
        timeout: HTTPTimeout,
    ) -> HTTPResponse:
        """This is the next function of the middleware."""
        return HTTPResponse(200, {"Foo": "Bar"}, {"id": "1", "name": "alive"})


class SyncDummyTransport(SyncAbstractTransport):
    def __call__(
        self,
        req: HTTPRequest,
        client_name: str,
        path: str,
        timeout: HTTPTimeout,
    ) -> HTTPResponse:
        """This is the next function of the middleware."""
        return HTTPResponse(200, {"Foo": "Bar"}, {"id": "1", "name": "alive"})


@pytest.fixture
def dummy_async_client_factory() -> AsyncClientFactory[Any, Any]:
    return AsyncClientFactory(
        sd=AsyncRouterDiscovery(), transport=AsyncDummyTransport()
    )


@pytest.fixture
def dummy_sync_client_factory() -> SyncClientFactory[Any, Any]:
    return SyncClientFactory(sd=SyncRouterDiscovery(), transport=SyncDummyTransport())
