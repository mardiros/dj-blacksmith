from typing import Any, List, Tuple

from blacksmith.domain.model import HTTPRequest, HTTPResponse
from blacksmith.domain.model.middleware.http_cache import (
    AbstractCachePolicy,
    AbstractSerializer,
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
