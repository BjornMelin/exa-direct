"""Pytest configuration: inject lightweight stubs for external modules if missing.

This keeps unit/integration tests hermetic without network or third-party installs.
"""

from __future__ import annotations

import sys
from types import ModuleType
from typing import Any


def _install_requests_stub() -> None:
    if "requests" in sys.modules:
        return
    m = ModuleType("requests")

    class RequestException(Exception):
        pass

    class HTTPError(RequestException):
        def __init__(self, response: Any | None = None, *args: Any) -> None:
            super().__init__(*args)
            self.response = response

    class Response:  # minimal
        def __init__(self) -> None:
            self.status_code = 200
            self.headers: dict[str, str] = {}
            self._content = b"{}"

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise HTTPError(self)

    m.RequestException = RequestException  # type: ignore[attr-defined]
    m.HTTPError = HTTPError  # type: ignore[attr-defined]
    m.Response = Response  # type: ignore[attr-defined]
    sys.modules["requests"] = m


def _install_httpx_stub() -> None:
    if "httpx" in sys.modules:
        return
    m = ModuleType("httpx")

    class RequestError(Exception):
        pass

    class HTTPStatusError(RequestError):
        def __init__(self, message: str, response: Any) -> None:
            super().__init__(message)
            self.response = response

    class Response:
        def __init__(self, status_code: int = 200, text: str = "{}") -> None:
            self.status_code = status_code
            self.text = text

        def json(self) -> Any:
            import json

            return json.loads(self.text)

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise HTTPStatusError("error", self)

    class Client:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def post(self, url: str, json: dict[str, Any]) -> Response:
            del url, json
            return Response(200, "{}")

    m.RequestError = RequestError  # type: ignore[attr-defined]
    m.HTTPStatusError = HTTPStatusError  # type: ignore[attr-defined]
    m.Response = Response  # type: ignore[attr-defined]
    m.Client = Client  # type: ignore[attr-defined]
    sys.modules["httpx"] = m


_install_requests_stub()
_install_httpx_stub()
