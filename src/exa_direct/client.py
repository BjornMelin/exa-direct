# pylint: disable=no-member
"""Thin wrapper around the Exa API for CLI usage.

This module provides a high-level interface to Exa API endpoints, including
search, contents retrieval, research tasks, and code context queries. It wraps
the official exa_py SDK with additional functionality for CLI operations.
"""

from __future__ import annotations

import dataclasses
import json
import os
import time
from collections.abc import Iterable, Iterator, Mapping, MutableMapping
from typing import Any, cast

from dotenv import load_dotenv

import httpx
from exa_py import Exa

from . import structured_logging

# API endpoints
_API_BASE = "https://api.exa.ai"
_RESEARCH_BASE = f"{_API_BASE}/research/v1"

LOGGER = structured_logging.get_logger(__name__)
_HTTP_TIMEOUT_SECONDS = 60.0


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

    def __init__(self, api_key: str, *, http: httpx.Client | None = None) -> None:
        """Initialize service with an Exa SDK client and an HTTP client.

        Args:
            api_key: Exa API key used for authentication.
            http: Optional `httpx.Client` to reuse; if not provided, a client
                with HTTP/2 enabled and a total timeout is created.
        """
        self._api_key = api_key
        self._exa = Exa(api_key)
        # persistent HTTP client for non-SDK endpoints (Context). Enable HTTP/2
        # with a total timeout.
        self._http_provided = http is not None
        if http is not None:
            self._http = http
            self._http2_enabled = bool(getattr(http, "http2", False))
        else:
            self._http, self._http2_enabled = _create_http_client(api_key)

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
        self,
        *,
        query: str,
        search_params: Mapping[str, Any] | None,
        content_params: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Search and retrieve contents in one call via SDK, including filters."""
        payload: dict[str, Any] = {}
        if search_params:
            payload.update(search_params)
        payload.update(content_params)
        response = self._exa.search_and_contents(query, **payload)
        return _to_dict(response)

    # pylint: disable=too-many-locals
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
        metadata: bool | Mapping[str, Any] | None = None,
        filter_empty_results: bool | None = None,
        flags: Iterable[str] | None = None,
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
        if metadata is not None:
            payload["metadata"] = metadata
        if filter_empty_results is not None:
            payload["filter_empty_results"] = filter_empty_results
        if flags:
            payload["flags"] = list(flags)

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
        self,
        *,
        url: str,
        find_params: Mapping[str, Any] | None,
        content_params: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Find similar and retrieve contents in one call via SDK, including filters."""
        payload: dict[str, Any] = {}
        if find_params:
            payload.update(find_params)
        payload.update(content_params)
        response = self._exa.find_similar_and_contents(url=url, **payload)
        return _to_dict(response)

    def answer(
        self,
        *,
        query: str,
        include_text: bool,
        model: Any | None = None,
        system_prompt: str | None = None,
        output_schema: dict[str, Any] | None = None,
        user_location: str | None = None,
    ) -> dict[str, Any]:
        """Generate an answer with citations.

        Args:
            query: Question to answer.
            include_text: Whether to include source text in response.
            model: Answer model (e.g., "exa" or "exa-pro").
            system_prompt: Optional system prompt for the answer model.
            output_schema: Optional JSON Schema dict for structured answers.
            user_location: Optional ISO country code for location-aware behavior.

        Returns:
            Dictionary containing answer and citations.
        """
        response = self._exa.answer(
            query=query,
            text=include_text,
            model=model,
            system_prompt=system_prompt,
            output_schema=output_schema,
            user_location=user_location,
        )
        return _to_dict(response)

    def answer_stream(
        self,
        *,
        query: str,
        include_text: bool,
        model: Any | None = None,
        system_prompt: str | None = None,
        output_schema: dict[str, Any] | None = None,
        user_location: str | None = None,
    ) -> Iterator[str]:
        """Stream an answer via the SDK, yielding text chunks."""
        stream = self._exa.stream_answer(
            query,
            text=include_text,
            model=model,
            system_prompt=system_prompt,
            output_schema=output_schema,
            user_location=user_location,
        )
        for chunk in stream:
            yield str(chunk)

    # --- Research API ---

    def research_start(
        self,
        *,
        instructions: str,
        model: str | None = None,
        output_schema: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a research task.

        Args:
            instructions: Natural-language instructions for the research agent.
            model: Research model (e.g., 'exa-research-fast', 'exa-research',
                'exa-research-pro').
            output_schema: Optional JSON Schema dict for structured output.

        Returns:
            Dictionary containing task details and ID.
        """
        # Build task parameters and call SDK.
        params: dict[str, Any] = {
            "instructions": instructions,
            "output_schema": output_schema,
            "model": model,
        }
        clean = {k: v for k, v in params.items() if v is not None}
        task = self._exa.research.create(**clean)
        return _to_dict(task)

    def research_get(self, *, research_id: str, events: bool = False) -> dict[str, Any]:
        """Return research task details using the SDK."""
        # Align with exa_py ResearchClient.get(research_id, *, events=False, ...)
        result = self._exa.research.get(research_id, events=events)
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
        result = self._exa.research.list(limit=limit, cursor=cursor)
        return _to_dict(result)

    def research_poll(self, *, research_id: str) -> dict[str, Any]:
        """Poll to completion using SDK defaults (no local timing knobs)."""
        # exa_py ResearchClient.poll_until_finished defaults:
        #   poll_interval=1000ms, timeout_ms=600000ms, events=False.
        # Rely on SDK defaults; pass positional research_id.
        details = self._exa.research.poll_until_finished(research_id)
        return _to_dict(details)

    def research_stream(self, *, research_id: str) -> Iterator[dict[str, Any]]:
        """Yield typed research events as JSON-serializable dicts.

        Uses the SDK's typed streaming (research.get(stream=True)) and converts
        each Pydantic event into a plain dict, suitable for JSON-lines output.
        """
        events = self._exa.research.get(research_id, stream=True)
        for event in events:
            if hasattr(event, "model_dump"):
                yield event.model_dump()
            else:
                # Best-effort fallback if the SDK returns non-Pydantic objects
                try:
                    yield json.loads(json.dumps(event, default=lambda o: o.__dict__))
                except Exception as exc:  # pragma: no cover - defensive fallback
                    msg = f"Unserializable research event: {event!r}"
                    raise TypeError(msg) from exc

    def answer_stream_json(
        self,
        *,
        query: str,
        include_text: bool,
        model: Any | None = None,
        system_prompt: str | None = None,
        output_schema: dict[str, Any] | None = None,
        user_location: str | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Stream answer chunks as JSON-line dicts.

        Each yielded item has the form {"event": "chunk", "data": <text>} and a
        final {"event": "done"} sentinel for consumers that need a terminator.
        """
        for chunk in self._exa.stream_answer(
            query,
            text=include_text,
            model=model,
            system_prompt=system_prompt,
            output_schema=output_schema,
            user_location=user_location,
        ):
            yield {"event": "chunk", "data": str(chunk)}
        yield {"event": "done"}

    # --- Context (Exa Code) ---

    def context(
        self, *, query: str, tokens_num: str | int | None = None
    ) -> dict[str, Any]:
        """Call the Context API to retrieve code-focused results.

        Args:
            query: Code-related query text.
            tokens_num: Maximum tokens to return ("dynamic" or integer).

        Returns:
            JSON object returned by the service.
        """
        # Build request payload
        payload: dict[str, Any] = {"query": query}
        if tokens_num is not None:
            payload["tokensNum"] = tokens_num

        # Lightweight retries with short exponential backoff on transient failures
        backoffs = [0.1, 0.2, 0.5]
        url = f"{_API_BASE}/context"

        for delay in backoffs:
            try:
                resp = self._http.post(url, json=payload)
                resp.raise_for_status()
                return resp.json()  # Success: return parsed JSON response.
            except httpx.HTTPStatusError as exc:
                # Retry only on server errors (HTTP 5xx). Raise otherwise.
                status = getattr(getattr(exc, "response", None), "status_code", 0)
                if int(status) >= 500:
                    time.sleep(delay)
                else:
                    raise
            except httpx.RequestError as exc:
                if self._downgrade_on_http2_error(exc):
                    continue
                time.sleep(delay)  # Network-level error: sleep and retry

        # Final attempt
        try:
            resp = self._http.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as exc:
            if self._downgrade_on_http2_error(exc):
                resp = self._http.post(url, json=payload)
                resp.raise_for_status()
                return resp.json()
            raise

    def close(self) -> None:
        """Close the internally managed HTTP client."""
        if not self._http_provided:
            self._http.close()

    def __enter__(self) -> ExaService:
        """Return self for context manager usage."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Ensure resources are cleaned up when exiting context."""
        del exc_type, exc, tb
        self.close()

    def _downgrade_on_http2_error(self, error: Exception) -> bool:
        """Downgrade to HTTP/1 when HTTP/2 connectivity fails.

        Args:
            error: The triggering request error.

        Returns:
            True when the client was rebuilt, False otherwise.
        """
        if self._http_provided or not getattr(self, "_http2_enabled", False):
            return False
        if not _is_http2_negotiation_error(error):
            return False
        self._http.close()
        self._http, self._http2_enabled = _create_http_client(
            self._api_key, prefer_http2=False
        )
        LOGGER.warning(
            "http_client.http2_downgraded",
            reason=str(error),
            message="Exa context transport downgraded to HTTP/1.1",
        )
        return True


def _create_http_client(
    api_key: str, *, prefer_http2: bool = True
) -> tuple[httpx.Client, bool]:
    """Create an httpx client preferring HTTP/2 with graceful fallback."""
    common_kwargs: dict[str, Any] = {
        "timeout": _HTTP_TIMEOUT_SECONDS,
        "headers": {"x-api-key": api_key},
    }
    if not prefer_http2:
        client = httpx.Client(http2=False, **common_kwargs)
        return client, False
    try:
        client = httpx.Client(http2=True, **common_kwargs)
        return client, True
    except (ImportError, AttributeError, httpx.UnsupportedProtocol) as exc:
        LOGGER.warning(
            "http_client.http2_unavailable",
            reason=str(exc),
            message="Falling back to HTTP/1.1 transport.",
        )
        return _create_http_client(api_key, prefer_http2=False)


def _is_http2_negotiation_error(error: Exception) -> bool:
    """Return True when the error indicates an HTTP/2 negotiation failure."""
    http2_related = (
        httpx.RemoteProtocolError,
        httpx.LocalProtocolError,
        httpx.UnsupportedProtocol,
    )
    if isinstance(error, http2_related):
        return True
    text = str(error).upper()
    return "HTTP/2" in text or "ALPN" in text or "H2" in text


def resolve_api_key(explicit: str | None) -> str:
    """Resolve the Exa API key from CLI flag or environment variable."""
    # Check explicit key first
    if explicit:
        return explicit

    load_dotenv()

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

    # Handle dataclass responses from newer exa_py releases
    if dataclasses.is_dataclass(response) and not isinstance(response, type):
        return dataclasses.asdict(response)

    # Handle mapping-like objects
    if isinstance(response, Mapping):
        return dict(response)

    # Unsupported type
    raise TypeError(f"Unsupported response type: {type(response)!r}")
