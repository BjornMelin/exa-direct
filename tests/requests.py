"""Minimal test stub for the `requests` package.

This stub provides just enough surface for unit tests that construct
`requests.Response` instances and for modules that import `requests`
for exception types. It does not perform any I/O.
"""

from __future__ import annotations

from collections.abc import Iterator
from types import MethodType
from typing import Any


class RequestException(Exception):
    """Base request exception (stub)."""


class HTTPError(RequestException):
    """HTTP error exception (stub)."""

    def __init__(self, *args: Any, response: Response | None = None) -> None:
        """Initialize the HTTPError with an optional response stub."""
        super().__init__(*args)
        self.response = response


class Response:
    """Lightweight Response stub with mutable attributes."""

    def __init__(self) -> None:
        """Initialize default fields; tests patch `iter_lines` as needed."""
        self.status_code: int = 200
        self.headers: dict[str, str] = {}
        self._content: bytes = b""

        # `iter_lines` will be patched by tests via MethodType
        def _default_iter_lines(_self: Response, decode_unicode: bool) -> Iterator[str]:
            del decode_unicode
            return iter(())

        object.__setattr__(
            self,
            "iter_lines",
            MethodType(_default_iter_lines, self),
        )

    def raise_for_status(self) -> None:
        """Raise HTTPError when status_code >= 400 (stub)."""
        if self.status_code >= 400:
            raise HTTPError(self)


class Session:
    """Minimal Session stub used by tests to monkeypatch `get`."""

    def get(self, *args: Any, **kwargs: Any):  # pragma: no cover - only patched over
        """Placeholder; tests patch this method via monkeypatch."""
        raise NotImplementedError
