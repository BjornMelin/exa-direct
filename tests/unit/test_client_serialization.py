"""Tests for serializing exa_py dataclass responses via `_to_dict`."""
# pylint: disable=protected-access

from __future__ import annotations

from exa_py.api import AnswerResponse, AnswerResult, Result, SearchResponse

from exa_direct import client as client_module


def test_to_dict_handles_search_response_dataclass() -> None:
    """Ensure `_to_dict` normalizes search dataclass payloads."""
    response = SearchResponse(
        results=[Result(url="https://example.com", id="doc-1", title="Example")],
        autoprompt_string="Example query",
        resolved_search_type="auto",
        auto_date="2025-10-22",
        context="context payload",
        statuses=None,
        cost_dollars=None,
    )

    data = client_module._to_dict(response)

    assert data["autoprompt_string"] == "Example query"
    assert data["resolved_search_type"] == "auto"
    assert data["results"][0]["url"] == "https://example.com"
    assert data["results"][0]["title"] == "Example"


def test_to_dict_handles_nested_dataclasses() -> None:
    """Ensure nested dataclasses (answer citations) are converted recursively."""
    response = AnswerResponse(
        answer={"summary": "Hello"},
        citations=[
            AnswerResult(
                id="cite-1",
                url="https://example.com/article",
                title="Article",
                published_date="2025-10-01",
                author="Reporter",
                text="Full text",
            )
        ],
    )

    data = client_module._to_dict(response)

    assert data["answer"]["summary"] == "Hello"
    assert data["citations"][0]["id"] == "cite-1"
    assert data["citations"][0]["url"] == "https://example.com/article"
