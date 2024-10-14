from typing import Any

import prometheus_client  # type: ignore
import pytest
from blacksmith import (
    AsyncClientFactory,
    AsyncRouterDiscovery,
    SyncClientFactory,
    SyncRouterDiscovery,
)
from django.test import RequestFactory

from .fixtures import AsyncDummyTransport, SyncDummyTransport


@pytest.fixture
def req():
    return RequestFactory()


@pytest.fixture
def prometheus_registry():
    prometheus_client.REGISTRY = prometheus_client.CollectorRegistry()
    yield prometheus_client.REGISTRY


@pytest.fixture
def dummy_async_client_factory() -> AsyncClientFactory[Any]:
    return AsyncClientFactory(
        sd=AsyncRouterDiscovery(), transport=AsyncDummyTransport()
    )


@pytest.fixture
def dummy_sync_client_factory() -> SyncClientFactory[Any]:
    return SyncClientFactory(sd=SyncRouterDiscovery(), transport=SyncDummyTransport())
