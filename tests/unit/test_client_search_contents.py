"""Unit tests for combining search filters with contents options."""

from __future__ import annotations

from typing import Any

import pytest

from exa_direct import client as client_module


def test_search_and_contents_merges_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure search filters and contents options are merged and forwarded."""
    captured: dict[str, Any] = {}

    def _sac(query: str, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
        nonlocal captured
        captured = {"query": query, **kwargs}
        return {"results": []}

    svc = client_module.ExaService("k")
    monkeypatch.setattr(
        svc, "_exa", type("X", (), {"search_and_contents": staticmethod(_sac)})
    )

    filters = {"type": "neural", "num_results": 5, "include_domains": ["exa.ai"]}
    contents = {"text": True, "summary": {"query": "key points"}}
    out = svc.search_and_contents(
        query="AGI state", search_params=filters, content_params=contents
    )
    assert out == {"results": []}
    assert captured["query"] == "AGI state"
    assert captured["type"] == "neural"
    assert captured["num_results"] == 5
    assert captured["include_domains"] == ["exa.ai"]
    assert captured["text"] is True
    assert captured["summary"]["query"] == "key points"


def test_find_similar_and_contents_merges_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure find filters and contents options are merged and forwarded."""
    captured: dict[str, Any] = {}

    def _fsac(url: str, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
        nonlocal captured
        captured = {"url": url, **kwargs}
        return {"results": []}

    svc = client_module.ExaService("k")
    monkeypatch.setattr(
        svc,
        "_exa",
        type("X", (), {"find_similar_and_contents": staticmethod(_fsac)}),
    )

    filters = {"exclude_source_domain": True, "include_domains": ["arxiv.org"]}
    contents = {"highlights": True}
    out = svc.find_similar_and_contents(
        url="https://example.com", find_params=filters, content_params=contents
    )
    assert out == {"results": []}
    assert captured["url"] == "https://example.com"
    assert captured["exclude_source_domain"] is True
    assert captured["include_domains"] == ["arxiv.org"]
    assert captured["highlights"] is True
