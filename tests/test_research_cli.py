"""Tests for research and context CLI commands."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Any

import pytest

from exa_direct import cli
from exa_direct import client as client_module


class DummyResearchService:
    """Dummy service capturing research calls."""

    def __init__(self) -> None:
        """Initialize the in-memory call log."""
        self.calls: list[dict[str, Any]] = []

    # minimal surface used by CLI dispatcher
    def research_start(
        self,
        *,
        instructions: str,
        model: str | None,
        output_schema: dict[str, Any] | None,
        infer_schema: bool,
    ) -> dict[str, Any]:
        """Record a research_start invocation."""
        self.calls.append(
            {
                "method": "research_start",
                "instructions": instructions,
                "model": model,
                "schema": output_schema,
                "infer": infer_schema,
            }
        )
        return {"id": "task-1"}

    def research_get(self, *, research_id: str, events: bool) -> dict[str, Any]:
        """Record a research_get invocation."""
        self.calls.append(
            {"method": "research_get", "id": research_id, "events": events}
        )
        payload: dict[str, Any] = {"id": research_id, "status": "running"}
        if events:
            payload["events"] = [{"event": "task_submitted"}]
        return payload

    def research_list(self, *, limit: int | None, cursor: str | None) -> dict[str, Any]:
        """Record a research_list invocation."""
        self.calls.append({"method": "research_list", "limit": limit, "cursor": cursor})
        return {"data": [], "hasMore": False}

    def research_poll(
        self, *, research_id: str, poll_interval: int, max_wait_time: int
    ) -> dict[str, Any]:
        """Record a research_poll invocation."""
        self.calls.append(
            {
                "method": "research_poll",
                "id": research_id,
                "interval": poll_interval,
                "timeout": max_wait_time,
            }
        )
        return {"id": research_id, "status": "completed", "data": {"ok": True}}

    def research_stream(self, *, research_id: str) -> Iterator[str]:
        """Record a research_stream invocation and yield fake SSE events."""
        self.calls.append({"method": "research_stream", "id": research_id})
        yield "event: running"
        yield 'data: {"progress": 50}'
        yield "event: completed"

    def context(self, *, query: str, tokens_num: str | int | None) -> dict[str, Any]:
        """Record a context query invocation."""
        self.calls.append({"method": "context", "query": query, "tokens": tokens_num})
        return {"response": "code examples here"}


@pytest.fixture(name="dummy_service")
def fixture_dummy_service(monkeypatch: pytest.MonkeyPatch) -> DummyResearchService:
    """Provide a patched research service capturing CLI interactions."""
    service = DummyResearchService()
    monkeypatch.setattr(client_module, "create_service", lambda _api_key: service)
    monkeypatch.setattr(client_module, "resolve_api_key", lambda explicit: "key")
    return service


def test_research_start(
    dummy_service: DummyResearchService, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI research start should call service and print task id."""
    exit_code = cli.main(
        [
            "research",
            "start",
            "--instructions",
            "Find latest GPU roadmaps",
            "--model",
            "exa-research-fast",
            "--infer-schema",
        ]
    )
    assert exit_code == 0
    out = json.loads(capsys.readouterr().out)
    assert out == {"id": "task-1"}
    assert dummy_service.calls[0]["method"] == "research_start"


def test_research_get_list_poll(dummy_service: DummyResearchService) -> None:
    """CLI subcommands get, list, poll should fan out to service methods."""
    assert cli.main(["research", "get", "--id", "abc"]) == 0
    assert cli.main(["research", "list", "--limit", "5"]) == 0
    assert cli.main(["research", "poll", "--id", "abc", "--model", "exa-research"]) == 0
    # ensure calls captured
    methods = [call["method"] for call in dummy_service.calls]
    assert methods[:3] == ["research_get", "research_list", "research_poll"]


def test_research_stream(
    dummy_service: DummyResearchService, capsys: pytest.CaptureFixture[str]
) -> None:
    """Streaming command should yield sequential SSE events."""
    exit_code = cli.main(["research", "stream", "--id", "abc"])
    assert exit_code == 0
    output = capsys.readouterr().out.strip().splitlines()
    assert output[0].startswith("event: running")
    assert output[-1].startswith("event: completed")
    assert dummy_service.calls[-1]["method"] == "research_stream"


def test_research_get_with_events(
    dummy_service: DummyResearchService, capsys: pytest.CaptureFixture[str]
) -> None:
    """`research get --events` should request event logs and print them."""
    exit_code = cli.main(["research", "get", "--id", "abc", "--events"])
    assert exit_code == 0
    call = dummy_service.calls[-1]
    assert call["method"] == "research_get"
    assert call["events"] is True
    out = json.loads(capsys.readouterr().out)
    assert out["events"][0]["event"] == "task_submitted"


def test_context_query(
    dummy_service: DummyResearchService, capsys: pytest.CaptureFixture[str]
) -> None:
    """Context query should emit JSON payload from service."""
    exit_code = cli.main(["context", "query", "--query", "pandas groupby"])
    assert exit_code == 0
    assert json.loads(capsys.readouterr().out) == {"response": "code examples here"}
    assert dummy_service.calls[-1]["method"] == "context"
