"""Minimal test stub for the `httpx` package."""

from __future__ import annotations

from typing import Any


class RequestError(Exception):
    """Base client exception (stub)."""


class HTTPStatusError(RequestError):
    """HTTP status error (stub)."""

    def __init__(self, message: str, response: Response) -> None:
        """Initialize error with associated response."""
        super().__init__(message)
        self.response = response


class Response:
    """Simplified response stub."""

    def __init__(self, status_code: int = 200, text: str = "{}") -> None:
        """Initialize response with status and text body."""
        self.status_code = status_code
        self.text = text

    def json(self) -> Any:  # pragma: no cover - not used in current tests
        """Return parsed JSON body."""
        import json

        return json.loads(self.text)

    def raise_for_status(self) -> None:
        """Raise HTTPStatusError for 4xx/5xx codes."""
        if self.status_code >= 400:
            raise HTTPStatusError("error", self)


class Client:
    """Minimal httpx.Client stub with a `post` method."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        """Initialize client (no-op in stub)."""

    def post(self, url: str, json: dict[str, Any]) -> Response:  # pragma: no cover
        """Return a default OK response."""
        del url, json
        return Response(200, "{}")
