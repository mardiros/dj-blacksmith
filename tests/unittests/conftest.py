import prometheus_client  # type: ignore
import pytest
from django.test import RequestFactory


@pytest.fixture
def req():
    return RequestFactory()


@pytest.fixture
def prometheus_registry():
    prometheus_client.REGISTRY = prometheus_client.CollectorRegistry()
    yield prometheus_client.REGISTRY
