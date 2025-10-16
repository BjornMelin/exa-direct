"""Thin wrapper around the Exa API for CLI usage."""

from __future__ import annotations

import os
from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from typing import Any

import requests
from exa_py import Exa

_API_BASE = "https://api.exa.ai"
_RESEARCH_BASE = f"{_API_BASE}/research/v1"


class ExaService:
    """Provides high-level helpers for Exa API endpoints."""

    def __init__(
        self, api_key: str, *, session: requests.Session | None = None
    ) -> None:
        """Initialize Exa service client.

        Args:
            api_key: Exa API key for authentication.
            session: Optional requests session for HTTP calls.

        """
        self._api_key = api_key
        self._exa = Exa(api_key)
        self._session = session or requests.Session()

    def search(self, *, query: str, params: Mapping[str, Any]) -> dict[str, Any]:
        """Execute the search endpoint."""
        response = self._exa.search(query, **params)
        return _to_dict(response)

    def contents(
        self,
        *,
        urls: Iterable[str],
        text: bool,
        highlights: bool,
        livecrawl: str | None,
    ) -> dict[str, Any]:
        """Fetch page contents for the provided URLs."""
        payload: MutableMapping[str, Any] = {"urls": list(urls)}
        if text:
            payload["text"] = True
        if highlights:
            payload["highlights"] = True
        if livecrawl:
            payload["livecrawl"] = livecrawl
        response = self._session.post(
            f"{_API_BASE}/contents",
            headers={
                "x-api-key": self._api_key,
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def find_similar(self, *, url: str, params: Mapping[str, Any]) -> dict[str, Any]:
        """Call the find_similar endpoint."""
        response = self._exa.find_similar(url=url, **params)
        return _to_dict(response)

    def answer(self, *, query: str, include_text: bool) -> dict[str, Any]:
        """Generate an answer with citations."""
        response = self._exa.answer(query=query, text=include_text)
        return _to_dict(response)

    # --- Research API ---

    def research_start(
        self,
        *,
        instructions: str,
        model: str | None = None,
        output_schema: Mapping[str, Any] | None = None,
        infer_schema: bool = False,
    ) -> dict[str, Any]:
        """Create a research task.

        Args:
            instructions: Natural-language instructions for the research agent.
            model: Research model (e.g., 'exa-research-fast', 'exa-research',
                'exa-research-pro').
            output_schema: Optional JSON Schema dict for structured output.
            infer_schema: Whether to infer a schema when none is provided.

        """
        params: dict[str, Any] = {
            "instructions": instructions,
            "output_schema": output_schema,
            "infer_schema": infer_schema,
        }
        if model:
            params["model"] = model
        task = self._exa.research.create_task(  # type: ignore[attr-defined]
            **{k: v for k, v in params.items() if v is not None}
        )
        return _to_dict(task)

    def research_get(self, *, research_id: str, events: bool = False) -> dict[str, Any]:
        """Get a research task (optionally with events)."""
        url = f"{_RESEARCH_BASE}/{research_id}"
        params: dict[str, Any] = {}
        if events:
            params["events"] = "true"
        resp = self._session.get(
            url,
            headers={"x-api-key": self._api_key},
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def research_list(
        self, *, limit: int | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """List research tasks with optional pagination."""
        return self._exa.research.list_tasks(  # type: ignore[attr-defined]
            limit=limit, cursor=cursor
        )

    def research_poll(
        self, *, research_id: str, poll_interval: int = 10, max_wait_time: int = 600
    ) -> dict[str, Any]:
        """Poll a research task until completion using SDK helper."""
        details = self._exa.research.poll_task(  # type: ignore[attr-defined]
            task_id=research_id,
            poll_interval=poll_interval,
            max_wait_time=max_wait_time,
        )
        return _to_dict(details)

    def research_stream(self, *, research_id: str) -> Iterator[str]:
        """Yield SSE lines for a research task stream endpoint."""
        url = f"{_RESEARCH_BASE}/{research_id}"
        with self._session.get(
            url,
            headers={
                "Accept": "text/event-stream",
                "x-api-key": self._api_key,
            },
            params={"stream": "true"},
            stream=True,
            timeout=300,
        ) as resp:
            resp.raise_for_status()
            for raw in resp.iter_lines(decode_unicode=True):
                if raw and (line := raw.strip()):
                    yield line

    # --- Context (Exa Code) ---

    def context(
        self, *, query: str, tokens_num: str | int | None = None
    ) -> dict[str, Any]:
        """Call the Context API to retrieve code-focused context."""
        payload: dict[str, Any] = {"query": query}
        if tokens_num is not None:
            payload["tokensNum"] = tokens_num
        resp = self._session.post(
            f"{_API_BASE}/context",
            headers={"x-api-key": self._api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()


def resolve_api_key(explicit: str | None) -> str:
    """Resolve the Exa API key from CLI flag or `EXA_API_KEY`."""
    if explicit:
        return explicit
    if env_key := os.getenv("EXA_API_KEY"):
        return env_key
    raise RuntimeError(
        "EXA_API_KEY is required; set the environment variable or use --api-key"
    )


def create_service(api_key: str) -> ExaService:
    """Instantiate an :class:`ExaService`."""
    return ExaService(api_key)


def _to_dict(response: Any) -> dict[str, Any]:
    """Return a dictionary representation from an Exa SDK response."""
    if hasattr(response, "model_dump"):
        return response.model_dump()
    if hasattr(response, "dict"):
        return response.dict()  # type: ignore[return-value]
    if isinstance(response, Mapping):
        return dict(response)
    raise TypeError(f"Unsupported response type: {type(response)!r}")
