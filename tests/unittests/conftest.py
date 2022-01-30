
import pytest
from django.test import RequestFactory


@pytest.fixture
def req():
    return RequestFactory()
