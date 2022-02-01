"""Middleware"""
import abc
from typing import Any, Mapping

from blacksmith import SyncHTTPMiddleware
from django.http.request import HttpRequest


class SyncAbstractMiddlewareFactoryBuilder(abc.ABC):
    """Build the factory"""

    @abc.abstractmethod
    def __init__(self, settings: Mapping[str, Any]):
        """Called when building the client associated to it."""

    @abc.abstractmethod
    def __call__(self, request: HttpRequest) -> SyncHTTPMiddleware:
        """Called on demand per request to build a client with this middleware"""
