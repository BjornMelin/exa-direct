"""Unit tests for research client behaviors (SDK-first, fallback, SSE)."""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import nullcontext
from types import MethodType, SimpleNamespace
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

    def _get(*, task_id: str, events: bool) -> dict[str, Any]:
        return {"id": task_id, "events": events, "status": "running"}

    svc = client_module.ExaService("k")
    monkeypatch.setattr(
        svc, "_exa", SimpleNamespace(research=SimpleNamespace(get=_get))
    )

    out = svc.research_get(research_id="abc", events=True)
    assert out == {"id": "abc", "events": True, "status": "running"}


def test_research_stream_events_parse(monkeypatch: pytest.MonkeyPatch) -> None:
    """research_stream_events should parse SSE into structured objects."""
    svc = client_module.ExaService("k")

    def _fake_get(
        _url: str,
        headers: dict[str, str],
        params: dict[str, Any],
        stream: bool,
        timeout: int,
    ):
        """Fake GET method."""
        assert params == {"stream": "true"}
        assert stream is True
        del headers
        del timeout
        lines = [
            "event: running",
            'data: {"progress": 50}',
            "",
            "event: completed",
            'data: {"ok": true}',
        ]

        response = _make_response(200, {})

        def _iter_lines(
            _self: requests.Response, decode_unicode: bool
        ) -> Iterator[str]:
            del decode_unicode
            yield from lines

        object.__setattr__(
            response,
            "iter_lines",
            MethodType(_iter_lines, response),
        )

        return nullcontext(response)

    monkeypatch.setattr(
        svc,
        "_session",
        type("_S", (), {"get": staticmethod(_fake_get)}),
    )

    events = list(svc.research_stream_events(research_id="abc"))
    assert events[0] == {"event": "running", "data": {"progress": 50}}
    assert events[-1] == {"event": "completed", "data": {"ok": True}}
