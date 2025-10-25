# pylint: disable=protected-access,no-member
"""Tests covering HTTP transport fallback behaviour."""

from __future__ import annotations

from typing import Any

import pytest

import httpx
from exa_direct import client as client_module


class _DummyClient:
    """Minimal httpx.Client stand-in used for transport tests."""

    def __init__(self, http2: bool, *, should_succeed: bool) -> None:
        """Store HTTP/2 capability and desired behaviour."""
        self.http2 = http2
        self.should_succeed = should_succeed
        self.closed = False
        self.calls: list[dict[str, Any]] = []

    def post(self, url: str, json: dict[str, Any]) -> Any:
        """Simulate either an HTTP/2 failure or a successful response."""
        self.calls.append({"url": url, "json": json})
        if self.should_succeed:
            return _Response({"ok": True})
        raise httpx.RemoteProtocolError("HTTP/2 negotiation failed")

    def close(self) -> None:
        """Mark the client as closed."""
        self.closed = True


class _Response:
    """Simple response wrapper matching the usage in the client."""

    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        """No-op for successful responses."""
        return

    def json(self) -> dict[str, Any]:
        """Return the stored payload."""
        return self._payload


def test_http_client_falls_back_when_http2_dependencies_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing HTTP/2 dependencies should trigger an HTTP/1 fallback."""
    created_args: list[bool] = []

    def _fake_client(*, http2: bool, **kwargs: Any) -> _DummyClient:
        del kwargs
        created_args.append(http2)
        if http2:
            raise ImportError("h2 not available")
        return _DummyClient(http2=False, should_succeed=True)

    monkeypatch.setattr(client_module.httpx, "Client", _fake_client)

    service = client_module.ExaService("api-key")

    assert created_args == [True, False]
    assert service._http2_enabled is False  # type: ignore[attr-defined]


def test_context_downgrades_from_http2_on_protocol_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Protocol errors during HTTP/2 usage should trigger a downgrade."""
    clients: list[_DummyClient] = []

    def _fake_client(*, http2: bool, **kwargs: Any) -> _DummyClient:
        del kwargs
        # First client (HTTP/2) fails, second (HTTP/1) succeeds.
        dummy = _DummyClient(http2=http2, should_succeed=not http2)
        clients.append(dummy)
        return dummy

    monkeypatch.setattr(client_module.httpx, "Client", _fake_client)
    monkeypatch.setattr(client_module.time, "sleep", lambda _: None)

    service = client_module.ExaService("api-key")
    result = service.context(query="embeddings")

    assert result == {"ok": True}
    assert len(clients) == 2
    assert clients[0].closed is True
    assert service._http2_enabled is False  # type: ignore[attr-defined]
