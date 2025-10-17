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

    def contents(self, *, urls: list[str], **options: Any) -> dict[str, Any]:
        """Record contents call and return mock response."""
        rec = {"method": "contents", "urls": urls, "options": options}
        self.calls.append(rec)
        return {"requestId": "abc"}

    def find_similar(self, *, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Record find_similar call and return mock response."""
        self.calls.append({"method": "find_similar", "url": url, "params": params})
        return {"results": ["example"]}

    def search_and_contents(
        self,
        *,
        query: str,
        search_params: dict[str, Any] | None,
        content_params: dict[str, Any],
    ) -> dict[str, Any]:
        """Record search_and_contents call and return mock response."""
        self.calls.append({
            "method": "search_and_contents",
            "query": query,
            "search_params": search_params,
            "content_params": content_params,
        })
        return {"results": []}

    def find_similar_and_contents(
        self,
        *,
        url: str,
        find_params: dict[str, Any] | None,
        content_params: dict[str, Any],
    ) -> dict[str, Any]:
        """Record find_similar_and_contents call and return mock response."""
        self.calls.append({
            "method": "find_similar_and_contents",
            "url": url,
            "find_params": find_params,
            "content_params": content_params,
        })
        return {"results": ["example"]}

    def answer_stream(
        self,
        *,
        query: str,
        include_text: bool,
        model: str | None = None,
        system_prompt: str | None = None,
        output_schema: dict[str, Any] | None = None,
        user_location: str | None = None,
    ) -> Any:
        """Yield streamed answer chunks."""
        self.calls.append({
            "method": "answer_stream",
            "query": query,
            "include_text": include_text,
            "model": model,
            "system_prompt": system_prompt,
            "output_schema": output_schema,
            "user_location": user_location,
        })
        yield "Paris"
        yield " is the capital of France."

    def answer(
        self,
        *,
        query: str,
        include_text: bool,
        model: str | None = None,
        system_prompt: str | None = None,
        output_schema: dict[str, Any] | None = None,
        user_location: str | None = None,
    ) -> dict[str, Any]:
        """Record answer call and return mock response."""
        self.calls.append({
            "method": "answer",
            "query": query,
            "include_text": include_text,
            "model": model,
            "system_prompt": system_prompt,
            "output_schema": output_schema,
            "user_location": user_location,
        })
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
    exit_code = cli.main([
        "search",
        "--query",
        "latest LLM research",
        "--type",
        "fast",
        "--num-results",
        "5",
    ])
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
    exit_code = cli.main([
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
    ])
    assert exit_code == 0
    stdout = capsys.readouterr().out
    assert json.loads(stdout) == {"requestId": "abc"}
    assert json.loads(output_path.read_text(encoding="utf-8")) == {"requestId": "abc"}
    assert dummy_service.calls[0]["method"] == "contents"
    assert dummy_service.calls[0]["urls"] == [
        "https://example.com",
        "https://another.example",
    ]
    assert dummy_service.calls[0]["options"]["text"] is True
    assert dummy_service.calls[0]["options"]["highlights"] is True
    assert dummy_service.calls[0]["options"]["livecrawl"] == "preferred"


def test_search_with_text_uses_search_and_contents(
    dummy_service: DummyService, capsys: pytest.CaptureFixture[str]
) -> None:
    """Search with --text should call search_and_contents."""
    exit_code = cli.main(["search", "--query", "DeepMind", "--text"])
    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {"results": []}
    call = dummy_service.calls[0]
    assert call["method"] == "search_and_contents"
    assert call["content_params"]["text"] is True
    # base search params should be present (even if empty)
    assert isinstance(call.get("search_params"), (dict, type(None)))


def test_find_similar_with_text_uses_find_similar_and_contents(
    dummy_service: DummyService, capsys: pytest.CaptureFixture[str]
) -> None:
    """find-similar with --text should call find_similar_and_contents."""
    exit_code = cli.main([
        "find-similar",
        "--url",
        "https://example.com",
        "--text",
    ])
    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {"results": ["example"]}
    call = dummy_service.calls[0]
    assert call["method"] == "find_similar_and_contents"
    assert call["content_params"]["text"] is True
    assert isinstance(call.get("find_params"), (dict, type(None)))


def test_answer_stream(
    dummy_service: DummyService, capsys: pytest.CaptureFixture[str]
) -> None:
    """Answer with --stream streams chunks to stdout."""
    exit_code = cli.main([
        "answer",
        "--query",
        "What is the capital of France?",
        "--stream",
    ])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Paris" in out and "capital of France" in out


def test_answer_stream_json_lines(
    dummy_service: DummyService, capsys: pytest.CaptureFixture[str]
) -> None:
    """Answer with --stream --json-lines emits JSON events per chunk."""

    # Monkeypatch the service to provide a JSON-lines stream
    def _answer_stream_json(
        *,
        query: str,
        include_text: bool,
        **kwargs: Any,
    ):  # type: ignore[override]
        del query, include_text, kwargs
        yield {"event": "chunk", "data": "Par"}
        yield {"event": "chunk", "data": "is"}
        yield {"event": "done"}

    dummy_service.answer_stream_json = _answer_stream_json  # type: ignore[attr-defined]
    exit_code = cli.main([
        "answer",
        "--query",
        "Where?",
        "--stream",
        "--json-lines",
    ])
    assert exit_code == 0
    lines = [json.loads(line) for line in capsys.readouterr().out.strip().splitlines()]
    assert lines[-1]["event"] == "done"


def test_find_similar_invokes_service(
    dummy_service: DummyService, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that find-similar command calls service correctly."""
    exit_code = cli.main([
        "find-similar",
        "--url",
        "https://example.com",
        "--num-results",
        "2",
        "--exclude-source-domain",
    ])
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
    exit_code = cli.main([
        "answer",
        "--query",
        "What is the capital of France?",
        "--include-text",
    ])
    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {"answer": "Paris", "citations": []}
    call = dummy_service.calls[0]
    assert call["method"] == "answer"
    assert call["query"] == "What is the capital of France?"
    assert call["include_text"] is True
