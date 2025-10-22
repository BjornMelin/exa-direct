"""Reusable workflow steps built on top of ExaService."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable, Mapping
from itertools import starmap
from typing import Any

import httpx

from ..client import ExaService


def run_search(
    service: ExaService,
    *,
    query: str,
    search_params: Mapping[str, Any] | None = None,
    contents_params: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute search or search_and_contents based on parameters."""
    if contents_params:
        return service.search_and_contents(
            query=query, search_params=search_params, content_params=contents_params
        )
    params = search_params or {}
    return service.search(query=query, params=params)


def run_find_similar(
    service: ExaService,
    *,
    url: str,
    find_params: Mapping[str, Any] | None = None,
    contents_params: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute find-similar or find-similar-and-contents."""
    if contents_params:
        return service.find_similar_and_contents(
            url=url, find_params=find_params, content_params=contents_params
        )
    params = find_params or {}
    return service.find_similar(url=url, params=params)


async def _fetch_single_content(
    service: ExaService,
    url: str,
    options: Mapping[str, Any],
    *,
    retries: int,
    backoff: float,
) -> dict[str, Any]:
    """Fetch contents for a single URL with exponential backoff retry logic."""
    # Retry until the maximum number of attempts is reached.
    for attempt in range(retries + 1):
        try:
            content_options = dict(options)
            content_options["urls"] = [url]
            # Fetch contents for the single URL.
            return await asyncio.to_thread(service.contents, **content_options)
        except (httpx.RequestError, httpx.HTTPStatusError, RuntimeError):
            if attempt == retries:
                # All retry attempts exhausted, re-raise the last exception
                raise

            # Calculate exponential backoff delay
            delay = backoff * (2**attempt)
            await asyncio.sleep(delay)

    # This should never be reached, but satisfies type checker
    raise RuntimeError(
        "Unexpected error: retry loop completed without success or failure"
    )


async def fetch_contents_parallel(
    service: ExaService,
    *,
    urls: Iterable[str],
    options: Mapping[str, Any],
    concurrency: int = 4,
    retries: int = 2,
    backoff: float = 0.5,
) -> list[dict[str, Any]]:
    """Fetch contents for multiple URLs using bounded concurrency."""
    url_list = list(urls)
    if not url_list:
        return []

    # Create a semaphore to limit concurrent HTTP requests.
    semaphore = asyncio.Semaphore(concurrency)
    results: list[dict[str, Any] | None] = [None] * len(url_list)

    # Define a worker function to fetch contents for a single URL.
    async def worker(idx: int, target: str) -> None:
        """Fetch contents for a single URL using retries and backoff."""
        async with semaphore:
            results[idx] = await _fetch_single_content(
                service, target, options, retries=retries, backoff=backoff
            )

    # Execute the worker functions for each URL in parallel.
    await asyncio.gather(*starmap(worker, enumerate(url_list)))
    return [item for item in results if item is not None]


def start_research(
    service: ExaService,
    *,
    instructions: str,
    model: str | None,
    schema: dict[str, Any] | None,
) -> dict[str, Any]:
    """Start a research task."""
    return service.research_start(
        instructions=instructions,
        model=model,
        output_schema=schema,
    )


def poll_research(service: ExaService, *, research_id: str) -> dict[str, Any]:
    """Poll a research task until completion."""
    return service.research_poll(research_id=research_id)


def get_research(
    service: ExaService, *, research_id: str, events: bool = False
) -> dict[str, Any]:
    """Fetch research status by ID."""
    return service.research_get(research_id=research_id, events=events)


def query_context(
    service: ExaService, *, query: str, tokens_num: str | int | None
) -> dict[str, Any]:
    """Call the context endpoint via ExaService."""
    return service.context(query=query, tokens_num=tokens_num)
