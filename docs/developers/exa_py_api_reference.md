# exa_py API Reference (Confirmed from Source)

This document captures the canonical SDK surfaces as implemented in `exa_py` (source review) to avoid drift from outdated web docs.

Scope: core sync `Exa` methods used by this CLI, and Research client methods under `exa_py.research.*`.

## Exa (sync)

- `search(query: str, *, type: Literal["auto","neural","keyword","fast"] = None, num_results: int = None, include_domains: list[str] = None, exclude_domains: list[str] = None, start_published_date: str = None, end_published_date: str = None, start_crawl_date: str = None, end_crawl_date: str = None, include_text: list[str] = None, exclude_text: list[str] = None, ...) -> SearchResponse`

- `search_and_contents(query: str, *, text: bool|dict = None, highlights: bool|dict = None, summary: dict = None, subpages: int = None, subpage_target: str|list[str] = None, extras: dict = None, context: bool|dict = None, livecrawl: Literal["always","preferred","fallback","never"] = None, livecrawl_timeout: int = None, ...) -> ContentsResponse`

- `get_contents(urls: list[str], *, text: bool|dict = None, highlights: bool|dict = None, summary: dict = None, subpages: int = None, subpage_target: str|list[str] = None, extras: dict = None, context: bool|dict = None, livecrawl: Literal["always","preferred","fallback","never"] = None, livecrawl_timeout: int = None) -> ContentsResponse`

- `find_similar(url: str, *, num_results: int = None, exclude_source_domain: bool = False, include_domains: list[str] = None, exclude_domains: list[str] = None) -> SearchResponse`

- `find_similar_and_contents(url: str, *, text: bool|dict = None, highlights: bool|dict = None, summary: dict = None, subpages: int = None, subpage_target: str|list[str] = None, extras: dict = None, context: bool|dict = None, livecrawl: Literal["always","preferred","fallback","never"] = None, livecrawl_timeout: int = None) -> ContentsResponse`

- `answer(query: str, *, text: bool = False) -> AnswerResponse`

- `stream_answer(query: str, *, text: bool = False) -> Iterable[str|bytes]` (yields chunks)

Notes:
- `text` may be `True` or an options dict: `{ include_html_tags: bool, max_characters: int }`.
- `highlights` dict keys: `{ num_sentences: int, highlights_per_url: int, query: str }`.
- `summary` dict keys: `{ query: str, schema: JSONSchemaDict }`.
- `context` may be `True` or `{ max_characters: int }`.

References: SDK cheat sheet and examples corroborate these names/options.

## Research (sync) — `exa_py.research`

- `create(*, instructions: str, model: Literal["exa-research-fast","exa-research","exa-research-pro"] = "exa-research-fast", output_schema: dict|pydantic.BaseModel|None = None) -> ResearchDto`
- `get(research_id: str, *, stream: bool = False, events: bool = False, output_schema: Type[pydantic.BaseModel]|None = None) -> ResearchDto | Generator[ResearchEvent, None, None] | ResearchTyped`
- `list(*, cursor: str|None = None, limit: int|None = None) -> ListResearchResponseDto`
- `poll_until_finished(research_id: str, *, poll_interval: int = 1000, timeout_ms: int = 600000, events: bool = False, output_schema: Type[pydantic.BaseModel]|None = None) -> ResearchDto|ResearchTyped`

Events are Pydantic models; when `stream=True`, `get` yields typed events. When `output_schema` is provided and the output is structured, `get`/`poll_until_finished` return a typed wrapper with `parsed_output`.

Defaults (from source): poll_interval=1000 ms, timeout_ms=600000, events=False.

## Context Endpoint (HTTP)

The `/context` API is not currently wrapped by `exa_py`; this CLI calls it directly with `httpx`:

```
POST /context
Headers: { "x-api-key": <API_KEY>, "Content-Type": "application/json" }
Body: { "query": "...", "tokensNum": "dynamic"|<int> }
```

We expose `exa context query --query "…" [--tokensNum dynamic|<int>]`.

## Compatibility Guarantees

- We removed legacy/fallback paths and only call final, supported SDK methods.
- All option names match the SDK’s current surface according to source review.
- If the SDK changes, tests will fail and this reference will be updated accordingly.

