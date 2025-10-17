"""Unit tests for research client behaviors (SDK-first, fallback, SSE)."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest

import requests
from exa_direct import client as client_module


def _make_response(status_code: int, payload: dict[str, Any]) -> requests.Response:
    """Construct a real requests.Response populated with the given payload."""
    response = requests.Response()
    response.status_code = status_code
    response.headers["Content-Type"] = "application/json"
    object.__setattr__(response, "_content", json.dumps(payload).encode("utf-8"))
    return response


def test_research_get_via_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    """research_get should call SDK 'get' directly."""

    def _get(research_id: str, *, events: bool) -> dict[str, Any]:
        return {"id": research_id, "events": events, "status": "running"}

    svc = client_module.ExaService("k")
    monkeypatch.setattr(
        svc, "_exa", SimpleNamespace(research=SimpleNamespace(get=_get))
    )

    out = svc.research_get(research_id="abc", events=True)
    assert out == {"id": "abc", "events": True, "status": "running"}


def test_research_stream_typed(monkeypatch: pytest.MonkeyPatch) -> None:
    """research_stream should yield dicts from typed SDK events."""
    svc = client_module.ExaService("k")

    class _E:
        def __init__(self, payload: dict[str, Any]) -> None:
            self._p = payload

        def model_dump(self) -> dict[str, Any]:
            """Return the stored payload; mimics Pydantic model_dump."""
            return self._p

    def _get(research_id: str, *, stream: bool = False, events: Any | None = None):
        del research_id, events
        assert stream is True
        yield _E({"eventType": "running"})
        yield _E({
            "eventType": "research-output",
            "output": {"outputType": "completed"},
        })

    monkeypatch.setattr(
        svc, "_exa", SimpleNamespace(research=SimpleNamespace(get=_get))
    )

    events = list(svc.research_stream(research_id="abc"))
    assert events[0]["eventType"] == "running"
    assert events[-1]["eventType"] == "research-output"
