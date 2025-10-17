"""Unit tests for answer options forwarded to the SDK."""

from __future__ import annotations

from typing import Any

import pytest

from exa_direct import client as client_module


def test_answer_forwards_options(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify answer forwards model/system_prompt/output_schema/user_location."""
    captured: dict[str, Any] = {}

    def _answer(**kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
        nonlocal captured
        captured = kwargs
        return {"answer": "ok", "citations": []}

    svc = client_module.ExaService("k")
    monkeypatch.setattr(svc, "_exa", type("X", (), {"answer": staticmethod(_answer)}))

    res = svc.answer(
        query="q",
        include_text=True,
        model="exa-pro",
        system_prompt="be terse",
        output_schema={"type": "object"},
        user_location="US",
    )
    assert res["answer"] == "ok"
    assert captured["query"] == "q"
    assert captured["text"] is True
    assert captured["model"] == "exa-pro"
    assert captured["system_prompt"] == "be terse"
    assert captured["output_schema"] == {"type": "object"}
    assert captured["user_location"] == "US"
