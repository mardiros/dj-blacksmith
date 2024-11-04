"""Middleware"""

import abc
from collections.abc import Mapping
from typing import Any

from blacksmith import AsyncHTTPAddHeadersMiddleware, AsyncHTTPMiddleware
from django.http.request import HttpRequest


class AsyncAbstractMiddlewareFactoryBuilder(abc.ABC):
    """Build the factory"""

    @abc.abstractmethod
    def __init__(self, settings: Mapping[str, Any]):
        """Called when building the client associated to it."""

    @abc.abstractmethod
    def __call__(self, request: HttpRequest) -> AsyncHTTPMiddleware:
        """Called on demand per request to build a client with this middleware"""


class AsyncForwardHeaderFactoryBuilder(AsyncAbstractMiddlewareFactoryBuilder):
    """
    Forward headers (every keys in kwargs)

    :param kwargs: headers
    """

    def __init__(self, settings: Mapping[str, Any]):
        self.headers: list[str] = settings["forwarded_headers"]

    def __call__(self, request: HttpRequest) -> AsyncHTTPAddHeadersMiddleware:
        headers: dict[str, str] = {}
        for hdr in self.headers:
            val: str = request.headers.get(hdr, "")  # type: ignore
            if val:
                headers[hdr] = val
        return AsyncHTTPAddHeadersMiddleware(headers)
