# Changelog

## 2025-10-17

### Added

- Structured Research SSE parsing in client: `research_stream_events()` returns `{event, data}` objects.
- CLI `research stream --json-events` to emit one JSON object per SSE event.
- CLI `answer --stream` to stream answer chunks via SDK.
- Rich contents options across commands (mapped to SDK fields):
  - `--text`, `--text-max-characters`, `--text-include-html-tags`
  - `--highlights`, `--highlights-num-sentences`, `--highlights-per-url`, `--highlights-query`
  - `--summary-query`, `--summary-schema @file`
  - `--subpages`, `--subpage-target`
  - `--extras-links`, `--extras-image-links`
  - `--context`, `--context-max-characters`
  - `--livecrawl [always|preferred|fallback|never]`, `--livecrawl-timeout`
- CLI auto-switch to combined endpoints when contents options are present:
  - `search` → `search_and_contents`
  - `find-similar` → `find_similar_and_contents`
- Examples and templates:
  - `examples/stream_consumer.sh` (pretty-prints `--json-events`)
  - `examples/research_instructions.md`, `examples/research_schema.json`
  - `.env.example` with `EXA_API_KEY`
- Docs (developer-facing): `docs/developers/exa_py_api_reference.md` capturing canonical SDK surfaces.
- ADRs: `ADR-0011 httpx over requests`, `ADR-0012 final SDK surface`, `ADR-0013 typed JSON-lines streaming`.

### Changed

- Standardized research SDK usage: `research.create(...)`, `research.get(...)`, `research.list(...)`.
- Standardized contents to SDK: `get_contents(...)` replaces raw HTTP.
- Client answer streaming now uses SDK `stream_answer(...)`.
- CLI routing extended with contents option builder and answer streaming branch.
- Docstrings normalized to concise Google-style; minor line wraps for readability.
- Research param alignment with latest exa_py:
  - `research_get` now calls `research.get(research_id, ...)` (no `task_id`).
  - `research_poll` relies on SDK defaults via `poll_until_finished(research_id)`.
  - Removed unsupported `--infer-schema` flag and corresponding service arg.
  - Kept `--preset` as a convenience hint; polling behavior remains SDK-default.
  - Switched research streaming to SDK typed events; CLI emits JSON-lines only.
  - Added `answer --stream --json-lines` for agent-friendly chunk events.
  - HTTP client: switch to `httpx.Client` for `/context` endpoint; unified error handling.

### Fixed

- Research endpoint correctness and headers retained for SSE; connection retries on
  initial SSE connect for transient statuses (429/502/503/504).
- Tests cover SDK-first research get, SSE parsing, CLI `--json-events`, and `answer --stream`.
- Tests updated for SDK-aligned research calls and simplified polling defaults.

### Removed

- Legacy research fallbacks and compatibility shims:
  - `create_task`/`get_task`/`list_tasks` probing; SDK-only now (final interface).
  - HTTP fallback for `research_get`.
- Unnecessary `_sleep` wrapper.

### Tooling / Dependencies

- Enforced SDK version supporting final research surface: `exa_py>=1.16.1,<2.0`.
- Runtime deps: `requests>=2.32,<3.0`.
- Dev deps: `ruff`, `pyright`, `pylint>=4.0.1,<5.0`, `pytest>=8.4.2,<9.0`.
- Ruff preview mode already enabled in `pyproject.toml`; lint/typing/test gates run in CI scripts locally.

### Documentation

- README: Research 2.0 quickstart; inline contents with search; rich contents options; streaming answers.
- AGENTS.md: Expanded agent routing to include rich contents options and `answer --stream`.
