"""Thin wrapper around the Exa API for CLI usage.

This module provides a high-level interface to Exa API endpoints, including
search, contents retrieval, research tasks, and code context queries. It wraps
the official exa_py SDK with additional functionality for CLI operations.
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from typing import Any, cast

import requests
from exa_py import Exa

# API endpoints
_API_BASE = "https://api.exa.ai"
_RESEARCH_BASE = f"{_API_BASE}/research/v1"


class ExaService:
    """Provides high-level helpers for Exa API endpoints.

    This class wraps the Exa API with convenient methods for search, contents
    retrieval, research tasks, and code context queries. It handles authentication,
    session management, and response formatting.

    Attributes:
        _api_key: The Exa API key used for authentication.
        _exa: The underlying Exa SDK client instance.
        _session: HTTP session for API calls.
    """

    def __init__(
        self, api_key: str, *, session: requests.Session | None = None
    ) -> None:
        """Initialize Exa service client.

        Args:
            api_key: Exa API key for authentication.
            session: Optional requests session for connection reuse.
        """
        self._api_key = api_key
        self._exa = Exa(api_key)
        self._session = session or requests.Session()

    def search(self, *, query: str, params: Mapping[str, Any]) -> dict[str, Any]:
        """Execute the search endpoint.

        Args:
            query: Search query string.
            params: Additional search parameters (type, filters, etc.).

        Returns:
            Dictionary containing search results.
        """
        response = self._exa.search(query, **params)
        return _to_dict(response)

    def search_and_contents(
        self, *, query: str, content_params: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Search and retrieve contents in one call via SDK."""
        response = self._exa.search_and_contents(query, **content_params)
        return _to_dict(response)

    def contents(
        self,
        *,
        urls: Iterable[str],
        text: bool | Mapping[str, Any] | None = None,
        highlights: Mapping[str, Any] | bool | None = None,
        summary: Mapping[str, Any] | None = None,
        subpages: int | None = None,
        subpage_target: str | list[str] | None = None,
        extras: Mapping[str, Any] | None = None,
        context: bool | Mapping[str, Any] | None = None,
        livecrawl: str | None = None,
        livecrawl_timeout: int | None = None,
    ) -> dict[str, Any]:
        """Fetch page contents using the SDK with rich options."""
        payload: MutableMapping[str, Any] = {"urls": list(urls)}
        if text is not None:
            payload["text"] = text
        if highlights:
            payload["highlights"] = highlights
        if summary:
            payload["summary"] = summary
        if subpages is not None:
            payload["subpages"] = subpages
        if subpage_target is not None:
            payload["subpage_target"] = subpage_target
        if extras:
            payload["extras"] = extras
        if context is not None:
            payload["context"] = context
        if livecrawl:
            payload["livecrawl"] = livecrawl
        if livecrawl_timeout is not None:
            payload["livecrawl_timeout"] = livecrawl_timeout

        response = self._exa.get_contents(**payload)
        return _to_dict(response)

    def find_similar(self, *, url: str, params: Mapping[str, Any]) -> dict[str, Any]:
        """Find pages similar to the given URL.

        Args:
            url: URL to find similar content for.
            params: Additional parameters (num_results, filters, etc.).

        Returns:
            Dictionary containing similar pages.
        """
        response = self._exa.find_similar(url=url, **params)
        return _to_dict(response)

    def find_similar_and_contents(
        self, *, url: str, content_params: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Find similar and retrieve contents in one call via SDK."""
        response = self._exa.find_similar_and_contents(url=url, **content_params)
        return _to_dict(response)

    def answer(self, *, query: str, include_text: bool) -> dict[str, Any]:
        """Generate an answer with citations.

        Args:
            query: Question to answer.
            include_text: Whether to include source text in response.

        Returns:
            Dictionary containing answer and citations.
        """
        response = self._exa.answer(query=query, text=include_text)
        return _to_dict(response)

    def answer_stream(self, *, query: str, include_text: bool) -> Iterator[str]:
        """Stream an answer via the SDK, yielding text chunks."""
        stream = self._exa.stream_answer(query, text=include_text)
        for chunk in stream:
            yield str(chunk)

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

        Returns:
            Dictionary containing task details and ID.
        """
        # Build task parameters and call SDK.
        params: dict[str, Any] = {
            "instructions": instructions,
            "output_schema": output_schema,
            "infer_schema": infer_schema,
            "model": model,
        }
        clean = {k: v for k, v in params.items() if v is not None}
        task = self._exa.research.create(**clean)  # type: ignore[attr-defined]
        return _to_dict(task)

    def research_get(self, *, research_id: str, events: bool = False) -> dict[str, Any]:
        """Return research task details using the SDK."""
        result = self._exa.research.get(task_id=research_id, events=events)  # type: ignore[attr-defined]
        return _to_dict(result)

    def research_list(
        self, *, limit: int | None = None, cursor: str | None = None
    ) -> dict[str, Any]:
        """List research tasks with optional pagination.

        Args:
            limit: Maximum number of tasks to return.
            cursor: Pagination cursor for fetching next page.

        Returns:
            Dictionary containing list of research tasks.
        """
        result = self._exa.research.list(limit=limit, cursor=cursor)  # type: ignore[attr-defined]
        return _to_dict(result)

    def research_poll(
        self,
        *,
        research_id: str,
        poll_interval: int = 10,
        max_wait_time: int = 600,
    ) -> dict[str, Any]:
        """Poll a research task until completion using SDK helper.

        Args:
            research_id: Unique identifier for the research task.
            poll_interval: Seconds to wait between status checks.
            max_wait_time: Maximum seconds to wait for completion.

        Returns:
            Dictionary containing final task results.
        """
        details = self._exa.research.poll_task(  # type: ignore[attr-defined]
            task_id=research_id,
            poll_interval=poll_interval,
            max_wait_time=max_wait_time,
        )
        return _to_dict(details)

    def research_stream(self, *, research_id: str) -> Iterator[str]:
        """Yield raw SSE lines for a research task stream endpoint."""
        url = f"{_RESEARCH_BASE}/{research_id}"

        # Configure retry delays for connection issues
        backoffs = (0.5, 1.0, 2.0)

        # Attempt connection with exponential backoff
        for delay in (*backoffs, None):
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
                # Retry on transient connection errors
                if resp.status_code in (429, 502, 503, 504) and delay is not None:
                    _sleep(delay)
                    continue

                resp.raise_for_status()

                # Stream and yield event lines
                for raw in resp.iter_lines(decode_unicode=True):
                    if raw and (line := raw.strip()):
                        yield line
                break

    def research_stream_events(self, *, research_id: str) -> Iterator[dict[str, Any]]:
        """Yield structured SSE events as dictionaries.

        Parses raw server-sent events into structured format with event names
        and parsed JSON data payloads when possible.

        Args:
            research_id: Unique identifier for the research task.

        Yields:
            Dictionary containing 'event' name and 'data' payload.
        """
        # Track current event being built
        current: dict[str, Any] = {}

        # Parse each raw SSE line
        for line in self.research_stream(research_id=research_id):
            if line.startswith("event:"):
                # Extract event name and yield previous event if complete
                name = line[len("event:") :].strip()
                if current:
                    yield current
                current = {"event": name}

            elif line.startswith("data:"):
                # Extract and parse data payload
                payload = line[len("data:") :].strip()
                try:
                    current["data"] = json.loads(payload)
                except json.JSONDecodeError:
                    # Fallback to raw string if JSON parsing fails
                    current["data"] = payload

        # Yield final event if present
        if current:
            yield current

    # --- Context (Exa Code) ---

    def context(
        self, *, query: str, tokens_num: str | int | None = None
    ) -> dict[str, Any]:
        """Call the Context API to retrieve code-focused context.

        Args:
            query: Code-related query for context retrieval.
            tokens_num: Maximum number of tokens to return.

        Returns:
            Dictionary containing code context and examples.
        """
        # Build request payload
        payload: dict[str, Any] = {"query": query}
        if tokens_num is not None:
            payload["tokensNum"] = tokens_num

        # Make API request
        resp = self._session.post(
            f"{_API_BASE}/context",
            headers={"x-api-key": self._api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()


def resolve_api_key(explicit: str | None) -> str:
    """Resolve the Exa API key from CLI flag or environment variable."""
    # Check explicit key first
    if explicit:
        return explicit

    # Check environment variable
    if env_key := os.getenv("EXA_API_KEY"):
        return env_key

    # No key found
    raise RuntimeError(
        "EXA_API_KEY is required; set the environment variable or use --api-key"
    )


def create_service(api_key: str) -> ExaService:
    """Instantiate an ExaService."""
    return ExaService(api_key)


def _to_dict(response: Any) -> dict[str, Any]:
    """Convert an Exa SDK response to a dictionary."""
    # Try Pydantic-style model_dump first
    if hasattr(response, "model_dump"):
        return response.model_dump()

    # Try dict() method for older SDK versions
    if hasattr(response, "dict"):
        raw = cast(Mapping[str, Any], response.dict())
        return dict(raw)

    # Handle mapping-like objects
    if isinstance(response, Mapping):
        return dict(response)

    # Unsupported type
    raise TypeError(f"Unsupported response type: {type(response)!r}")


def _sleep(seconds: float) -> None:
    """Sleep for the specified number of seconds."""
    time.sleep(seconds)
