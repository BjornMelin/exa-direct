"""Tests for the exa CLI entry points."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from exa_direct import cli
from exa_direct import client as client_module


class DummyService:
    """Collects calls for assertions."""

    def __init__(self) -> None:
        """Initialize dummy service for testing."""
        self.calls: list[dict[str, Any]] = []

    def search(self, *, query: str, params: dict[str, Any]) -> dict[str, Any]:
        """Record search call and return mock response."""
        self.calls.append({"method": "search", "query": query, "params": params})
        return {"results": []}

    def contents(
        self,
        *,
        urls: list[str],
        text: bool,
        highlights: bool,
        livecrawl: str | None,
    ) -> dict[str, Any]:
        """Record contents call and return mock response."""
        self.calls.append(
            {
                "method": "contents",
                "urls": urls,
                "text": text,
                "highlights": highlights,
                "livecrawl": livecrawl,
            }
        )
        return {"requestId": "abc"}

    def find_similar(self, *, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Record find_similar call and return mock response."""
        self.calls.append({"method": "find_similar", "url": url, "params": params})
        return {"results": ["example"]}

    def answer(self, *, query: str, include_text: bool) -> dict[str, Any]:
        """Record answer call and return mock response."""
        self.calls.append(
            {"method": "answer", "query": query, "include_text": include_text}
        )
        return {"answer": "Paris", "citations": []}


@pytest.fixture(name="dummy_service")
def fixture_dummy_service(monkeypatch: pytest.MonkeyPatch) -> DummyService:
    """Create mock service fixture for CLI tests."""
    service = DummyService()
    monkeypatch.setattr(client_module, "create_service", lambda _api_key: service)
    monkeypatch.setattr(client_module, "resolve_api_key", lambda explicit: "key")
    return service


def test_search_invokes_service(
    dummy_service: DummyService, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that search command calls service correctly."""
    exit_code = cli.main(
        [
            "search",
            "--query",
            "latest LLM research",
            "--type",
            "fast",
            "--num-results",
            "5",
        ]
    )
    assert exit_code == 0
    captured = json.loads(capsys.readouterr().out)
    assert captured == {"results": []}
    assert dummy_service.calls == [
        {
            "method": "search",
            "query": "latest LLM research",
            "params": {"num_results": 5, "type": "fast"},
        }
    ]


def test_contents_invokes_service(
    tmp_path: Path, dummy_service: DummyService, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that contents command calls service correctly."""
    output_path = tmp_path / "result.json"
    exit_code = cli.main(
        [
            "--pretty",
            "--save",
            str(output_path),
            "contents",
            "https://example.com",
            "https://another.example",
            "--text",
            "--highlights",
            "--livecrawl",
            "preferred",
        ]
    )
    assert exit_code == 0
    stdout = capsys.readouterr().out
    assert json.loads(stdout) == {"requestId": "abc"}
    assert json.loads(output_path.read_text(encoding="utf-8")) == {"requestId": "abc"}
    assert dummy_service.calls == [
        {
            "method": "contents",
            "urls": ["https://example.com", "https://another.example"],
            "text": True,
            "highlights": True,
            "livecrawl": "preferred",
        }
    ]


def test_find_similar_invokes_service(
    dummy_service: DummyService, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that find-similar command calls service correctly."""
    exit_code = cli.main(
        [
            "find-similar",
            "--url",
            "https://example.com",
            "--num-results",
            "2",
            "--exclude-source-domain",
        ]
    )
    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {"results": ["example"]}
    assert dummy_service.calls == [
        {
            "method": "find_similar",
            "url": "https://example.com",
            "params": {"num_results": 2, "exclude_source_domain": True},
        }
    ]


def test_answer_invokes_service(
    dummy_service: DummyService, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that answer command calls service correctly."""
    exit_code = cli.main(
        [
            "answer",
            "--query",
            "What is the capital of France?",
            "--include-text",
        ]
    )
    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {"answer": "Paris", "citations": []}
    assert dummy_service.calls == [
        {
            "method": "answer",
            "query": "What is the capital of France?",
            "include_text": True,
        }
    ]
