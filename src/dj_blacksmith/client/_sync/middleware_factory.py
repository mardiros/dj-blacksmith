"""Middleware"""
import abc
from typing import Any, Dict, List, Mapping

from blacksmith import SyncHTTPAddHeadersMiddleware, SyncHTTPMiddleware
from django.http.request import HttpRequest


class SyncAbstractMiddlewareFactoryBuilder(abc.ABC):
    """Build the factory"""

    @abc.abstractmethod
    def __init__(self, settings: Mapping[str, Any]):
        """Called when building the client associated to it."""

    @abc.abstractmethod
    def __call__(self, request: HttpRequest) -> SyncHTTPMiddleware:
        """Called on demand per request to build a client with this middleware"""


class SyncForwardHeaderFactoryBuilder(SyncAbstractMiddlewareFactoryBuilder):
    """
    Forward headers (every keys in kwargs)

    :param kwargs: headers
    """

    def __init__(self, settings: Mapping[str, Any]):
        self.headers: List[str] = settings["forwarded_headers"]

    def __call__(self, request: HttpRequest) -> SyncHTTPAddHeadersMiddleware:
        headers: Dict[str, str] = {}
        for hdr in self.headers:
            val: str = request.headers.get(hdr, "")  # type: ignore
            if val:
                headers[hdr] = val
        return SyncHTTPAddHeadersMiddleware(headers)
