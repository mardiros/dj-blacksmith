from typing import Any, List, Mapping, Tuple

from blacksmith import AsyncHTTPAddHeadersMiddleware, AsyncHTTPMiddleware
from blacksmith.domain.model import HTTPRequest, HTTPResponse
from blacksmith.domain.model.middleware.http_cache import (
    AbstractCachePolicy,
    AbstractSerializer,
)
from django.http import HttpRequest

from dj_blacksmith.client._async.middleware_factory import (
    AsyncAbstractMiddlewareFactoryBuilder,
)


class DummyCachePolicy(AbstractCachePolicy):
    def handle_request(self, req: HTTPRequest, client_name: str, path: str):
        """A function to decide if the http request is cachable."""
        return False

    def get_vary_key(self, client_name: str, path: str, request: HTTPRequest):
        return ""

    def get_response_cache_key(
        self, client_name: str, path: str, req: HTTPRequest, vary: List[str]
    ):
        return ""

    def get_cache_info_for_response(
        self, client_name: str, path: str, req: HTTPRequest, resp: HTTPResponse
    ) -> Tuple[int, str, List[str]]:
        return (0, "", [])


class DummySerializer(AbstractSerializer):
    @staticmethod
    def loads(s: str) -> Any:
        return b""

    @staticmethod
    def dumps(obj: Any) -> str:
        return ""


class DummyMiddlewareFactory1(AsyncAbstractMiddlewareFactoryBuilder):
    def __init__(self, settings: Mapping[str, Any]):
        pass

    def __call__(self, request: HttpRequest) -> AsyncHTTPMiddleware:
        return AsyncHTTPAddHeadersMiddleware(headers={"x-mdlwr-1": "1"})

    def __eq__(self, ob: Any) -> bool:
        return ob.__class__ == self.__class__


class DummyMiddlewareFactory2(AsyncAbstractMiddlewareFactoryBuilder):
    def __init__(self, settings: Mapping[str, Any]):
        pass

    def __call__(self, request: HttpRequest) -> AsyncHTTPMiddleware:
        return AsyncHTTPAddHeadersMiddleware(headers={"x-mdlwr-2": "2"})

    def __eq__(self, ob: Any) -> bool:
        return ob.__class__ == self.__class__
