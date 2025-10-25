"""Reusable test doubles used across unit tests."""

from __future__ import annotations

from typing import Any


class StubService:
    """In-memory stand-in for :class:`exa_direct.client.ExaService`."""

    def __init__(self) -> None:
        """Initialise call trackers."""
        self.search_calls: list[tuple[str, dict[str, Any]]] = []
        self.contents_calls: list[tuple[tuple[str, ...], dict[str, Any]]] = []
        self.answer_calls: list[tuple[str, dict[str, Any]]] = []
        self.close_calls = 0

    def search(self, *, query: str, params: dict[str, Any]) -> dict[str, Any]:
        """Record search usage and return a synthetic payload."""
        self.search_calls.append((query, params))
        return {"query": query, "params": params}

    def search_and_contents(
        self,
        *,
        query: str,
        search_params: dict[str, Any],
        content_params: dict[str, Any],
    ) -> dict[str, Any]:
        """Record combined search/contents usage."""
        self.search_calls.append((query, search_params))
        return {
            "query": query,
            "search_params": search_params,
            "content_params": content_params,
        }

    def contents(self, *, urls: list[str], **options: Any) -> dict[str, Any]:
        """Record contents usage."""
        self.contents_calls.append((tuple(urls), options))
        return {"urls": list(urls), "options": options}

    def find_similar(self, *, url: str, params: dict[str, Any]) -> dict[str, Any]:
        """Return canned similarity data."""
        return {"url": url, "params": params}

    def find_similar_and_contents(
        self,
        *,
        url: str,
        find_params: dict[str, Any],
        content_params: dict[str, Any],
    ) -> dict[str, Any]:
        """Return canned similarity data with inline contents."""
        return {
            "url": url,
            "find_params": find_params,
            "content_params": content_params,
        }

    def answer(self, *, query: str, **options: Any) -> dict[str, Any]:
        """Record answer usage."""
        self.answer_calls.append((query, dict(options)))
        return {"query": query, "options": options}

    def close(self) -> None:
        """Mirror ExaService.close()."""
        self.close_calls += 1
