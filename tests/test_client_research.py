"""Unit tests for research client behaviors (SDK-first, fallback, SSE)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from exa_direct import client as client_module


class _FakeResp:
    """Minimal Response stub supporting .status_code/.json()/.raise_for_status()."""

    def __init__(self, status_code: int, payload: dict[str, Any]) -> None:
        """Initialize the fake response."""
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        """No-op unless error status is simulated in tests."""
        if 400 <= self.status_code:
            import requests

            raise requests.HTTPError(response=self)  # type: ignore[arg-type]

    def json(self) -> dict[str, Any]:
        """Return the payload as JSON."""
        return self._payload


class _CM:
    """Context manager for streaming GET that yields given lines."""

    def __init__(self, status_code: int, lines: list[str]) -> None:
        """Initialize the context manager."""
        self.status_code = status_code
        self._lines = lines

    def __enter__(self) -> _CM:
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Exit the context manager."""
        return

    def raise_for_status(self) -> None:
        """Raise an HTTPError if the status code is 400 or higher."""
        if 400 <= self.status_code:
            import requests

            raise requests.HTTPError(response=self)  # type: ignore[arg-type]

    def iter_lines(self, decode_unicode: bool) -> Iterator[str]:
        """Yield preloaded lines."""
        yield from self._lines


def test_research_get_via_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    """research_get should call SDK 'get' directly."""

    class _Research:
        """Fake research class."""

        def get(self, *, task_id: str, events: bool) -> dict[str, Any]:
            """Return payload."""
            return {"id": task_id, "events": events, "status": "running"}

    svc = client_module.ExaService("k")
    monkeypatch.setattr(svc, "_exa", type("_E", (), {"research": _Research()})())

    out = svc.research_get(research_id="abc", events=True)
    assert out == {"id": "abc", "events": True, "status": "running"}


def test_research_stream_events_parse(monkeypatch: pytest.MonkeyPatch) -> None:
    """research_stream_events should parse SSE into structured objects."""
    svc = client_module.ExaService("k")

    def _fake_get(
        url: str,
        headers: dict[str, str],
        params: dict[str, Any],
        stream: bool,
        timeout: int,
    ) -> _CM:
        """Fake GET method."""
        assert params == {"stream": "true"}
        lines = [
            "event: running",
            'data: {"progress": 50}',
            "",
            "event: completed",
            'data: {"ok": true}',
        ]
        return _CM(200, lines)

    monkeypatch.setattr(
        svc,
        "_session",
        type("_S", (), {"get": staticmethod(_fake_get)}),
    )

    events = list(svc.research_stream_events(research_id="abc"))
    assert events[0] == {"event": "running", "data": {"progress": 50}}
    assert events[-1] == {"event": "completed", "data": {"ok": True}}
