# exa_py API Reference (Confirmed from Source)

This reference captures the synchronous `exa_py` surface consumed by the CLI. Signatures and option
shapes are pulled from the current source so this document stays authoritative when public docs lag.

The `Exa` client returns typed SDK responses (`SearchResponse`, `ContentsResponse`, `AnswerResponse`)
that expose `.results`, `.contents`, and other structured fields; see SDK models for details.

## Exa Client (synchronous)

### `Exa.search`

Search the Exa index with optional filters.

```python
from exa_py import Exa

def search(
    query: str,
    *,
    type: Literal["auto", "neural", "keyword", "fast"] | None = None,
    num_results: int | None = None,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    start_published_date: str | None = None,
    end_published_date: str | None = None,
    start_crawl_date: str | None = None,
    end_crawl_date: str | None = None,
    include_text: list[str] | None = None,
    exclude_text: list[str] | None = None,
    **kwargs: Unpack["SearchOptions"]
) -> SearchResponse: ...
```

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `query` | `str` | — | Query text passed to Exa search. |
| `type` | `Literal["auto","neural","keyword","fast"] \| None` | `None` | Search mode override (`auto` recommended). |
| `num_results` | `int \| None` | `None` | Number of results to return (SDK default: 10). |
| `include_domains` | `list[str] \| None` | `None` | Whitelist of domains. |
| `exclude_domains` | `list[str] \| None` | `None` | Domains to omit from results. |
| `start_published_date` | `str \| None` | `None` | ISO date lower bound for published timestamp. |
| `end_published_date` | `str \| None` | `None` | ISO date upper bound for published timestamp. |
| `start_crawl_date` | `str \| None` | `None` | ISO date lower bound for crawl timestamp. |
| `end_crawl_date` | `str \| None` | `None` | ISO date upper bound for crawl timestamp. |
| `include_text` | `list[str] \| None` | `None` | Required substrings that must appear in the fetched text. |
| `exclude_text` | `list[str] \| None` | `None` | Substrings that must not appear. |
| `**kwargs` | `SearchOptions` | — | Future-safe keyword options supported by the SDK. |

### `Exa.search_and_contents`

Run search and retrieve content in a single request.

```python
def search_and_contents(
    query: str,
    *,
    text: bool | TextOptions | None = None,
    highlights: bool | HighlightsOptions | None = None,
    summary: SummaryOptions | None = None,
    subpages: int | None = None,
    subpage_target: str | list[str] | None = None,
    extras: dict[str, Any] | None = None,
    context: bool | ContextOptions | None = None,
    livecrawl: Literal["always", "preferred", "fallback", "never"] | None = None,
    livecrawl_timeout: int | None = None,
    **kwargs: Unpack["SearchOptions"]
) -> ContentsResponse: ...
```

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `query` | `str` | — | Search text. |
| `text` | `bool \| TextOptions \| None` | `None` | Include raw text; `True` uses SDK defaults, `TextOptions` customises output. |
| `highlights` | `bool \| HighlightsOptions \| None` | `None` | Request highlight snippets per result. |
| `summary` | `SummaryOptions \| None` | `None` | Ask Exa to summarise results using a schema/query. |
| `subpages` | `int \| None` | `None` | Number of subpages to crawl per result. |
| `subpage_target` | `str \| list[str] \| None` | `None` | URL (or list) whose subpages should be retrieved. |
| `extras` | `dict[str, Any] \| None` | `None` | Experimental options forwarded to Exa. |
| `context` | `bool \| ContextOptions \| None` | `None` | Include language-model-ready context payload. |
| `livecrawl` | `Literal["always","preferred","fallback","never"] \| None` | `None` | Live crawling strategy for freshness vs. latency. |
| `livecrawl_timeout` | `int \| None` | `None` | Timeout (ms) for live crawl attempts. |
| `**kwargs` | `SearchOptions` | — | All search filters from `Exa.search`. |

### `Exa.get_contents`

Fetch content for known URLs or document IDs.

```python
def get_contents(
    urls: list[str],
    *,
    text: bool | TextOptions | None = None,
    highlights: bool | HighlightsOptions | None = None,
    summary: SummaryOptions | None = None,
    subpages: int | None = None,
    subpage_target: str | list[str] | None = None,
    extras: dict[str, Any] | None = None,
    context: bool | ContextOptions | None = None,
    livecrawl: Literal["always", "preferred", "fallback", "never"] | None = None,
    livecrawl_timeout: int | None = None
) -> ContentsResponse: ...
```

Parameters mirror `search_and_contents`, with `urls` replacing `query`.

### `Exa.find_similar`

Find similar pages for a given URL.

```python
def find_similar(
    url: str,
    *,
    num_results: int | None = None,
    exclude_source_domain: bool = False,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    **kwargs: Unpack["SearchOptions"]
) -> SearchResponse: ...
```

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `url` | `str` | — | Canonical URL whose neighbours you want. |
| `num_results` | `int \| None` | `None` | Number of similar documents (SDK default: 10). |
| `exclude_source_domain` | `bool` | `False` | Skip results from the same registrable domain. |
| `include_domains` | `list[str] \| None` | `None` | Domain allowlist for the similarity search. |
| `exclude_domains` | `list[str] \| None` | `None` | Domain blocklist. |
| `**kwargs` | `SearchOptions` | — | Additional filters (dates, categories, etc.). |

### `Exa.find_similar_and_contents`

Combine similarity search with content retrieval.

```python
def find_similar_and_contents(
    url: str,
    *,
    text: bool | TextOptions | None = None,
    highlights: bool | HighlightsOptions | None = None,
    summary: SummaryOptions | None = None,
    subpages: int | None = None,
    subpage_target: str | list[str] | None = None,
    extras: dict[str, Any] | None = None,
    context: bool | ContextOptions | None = None,
    livecrawl: Literal["always", "preferred", "fallback", "never"] | None = None,
    livecrawl_timeout: int | None = None,
    **kwargs: Unpack["SearchOptions"]
) -> ContentsResponse: ...
```

All options match `search_and_contents`, with `url` substituting for `query`.

### `Exa.answer`

Retrieve a synthesized answer for a query.

```python
def answer(
    query: str,
    *,
    text: bool = False
) -> AnswerResponse: ...
```

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `query` | `str` | — | Natural-language question to answer. |
| `text` | `bool` | `False` | When `True`, include supporting document text in the response payload. |

### `Exa.stream_answer`

Stream incremental answer chunks (text tokens or JSON segments).

```python
from collections.abc import Iterable

def stream_answer(
    query: str,
    *,
    text: bool = False
) -> Iterable[str | bytes]: ...
```

#### Streaming Answer Usage

```python
for chunk in exa.stream_answer("Summarise the latest Exa announcements", text=True):
    print(chunk, end="", flush=True)
```

Chunks are yielded as UTF-8 text (or bytes when structured). The SDK handles connection lifecycles; stop
iteration to cancel the stream.

### Shared option objects

| Option key | Shape | Notes |
| --- | --- | --- |
| `TextOptions` | `dict[str, bool \| int]` | Recognised keys: `include_html_tags: bool`, `max_characters: int`. |
| `HighlightsOptions` | `dict[str, int \| str]` | Keys: `num_sentences: int`, `highlights_per_url: int`, `query: str`. |
| `SummaryOptions` | `dict[str, Any]` | Keys: `query: str`, `schema: dict` (JSON Schema for structured outputs). |
| `ContextOptions` | `dict[str, int]` | Key: `max_characters: int` (token budget for LLM-ready context). |
| `SearchOptions` | Forward-compatible dict accepted by the SDK client. | Reserve for experimental flags surfaced upstream; avoid unless mirrored in CLI options. |

## Research Client (`exa_py.research`)

Import with `from exa_py import research`.

### `research.create`

```python
from exa_py import research

def create(
    *,
    instructions: str,
    model: Literal["exa-research-fast", "exa-research", "exa-research-pro"] = "exa-research-fast",
    output_schema: dict | pydantic.BaseModel | None = None
) -> ResearchDto: ...
```

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `instructions` | `str` | — | Task instructions for the long-form research run. |
| `model` | `Literal["exa-research-fast","exa-research","exa-research-pro"]` | `"exa-research-fast"` | Selects reasoning depth vs. latency. |
| `output_schema` | `dict \| pydantic.BaseModel \| None` | `None` | Optional JSON Schema or Pydantic model for typed results. |

Returns a `ResearchDto` describing the task.

### `research.get`

```python
def get(
    research_id: str,
    *,
    stream: bool = False,
    events: bool = False,
    output_schema: type[pydantic.BaseModel] | None = None
) -> ResearchDto | Generator[ResearchEvent, None, None] | ResearchTyped: ...
```

Behaviour depends on flags:

- `stream=True`: yields `ResearchEvent` objects.
- `events=True`: returns `ResearchDto` with `.events`.
- `output_schema` supplied: returns `ResearchTyped` with parsed data.

### `research.list`

```python
def list(
    *,
    cursor: str | None = None,
    limit: int | None = None
) -> ListResearchResponseDto: ...
```

Pagination mirrors REST defaults (SDK default `limit` is provider-defined).

### `research.poll_until_finished`

```python
def poll_until_finished(
    research_id: str,
    *,
    poll_interval: int = 1000,
    timeout_ms: int = 600_000,
    events: bool = False,
    output_schema: type[pydantic.BaseModel] | None = None
) -> ResearchDto | ResearchTyped: ...
```

| Name | Type | Default | Description |
| --- | --- | --- | --- |
| `poll_interval` | `int` | `1000` | Interval between status checks (milliseconds). |
| `timeout_ms` | `int` | `600000` | Maximum wait time before raising `TimeoutError`. |
| `events` | `bool` | `False` | When `True`, attaches event timeline to the returned DTO. |
| `output_schema` | `type[pydantic.BaseModel] \| None` | `None` | Parse structured output into the supplied Pydantic model. |

## HTTP Context Endpoint

The Context endpoint is not wrapped in `exa_py`; the CLI issues raw `httpx` calls.

```http
POST /context HTTP/1.1
Host: api.exa.ai
Content-Type: application/json
X-API-Key: <EXA_API_KEY>

{
  "query": "pandas groupby examples",
  "tokensNum": "dynamic"
}
```

CLI equivalent:

```bash
exa context query --query "pandas groupby examples" --tokensNum dynamic
```

## Compatibility Contract

- This document tracks the **final** surfaces used by the CLI—legacy or deprecated aliases are omitted.
- Option names and defaults reflect the current SDK implementation; upstream changes should trigger
  test failures and a doc sync.
- Shared option dictionaries (`text`, `highlights`, `summary`, `context`) are centralised above to
  reduce duplication and drift.
