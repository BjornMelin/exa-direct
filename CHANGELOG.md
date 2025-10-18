# Changelog

## [0.1.1] - 2025-10-18

### Documentation

- Rewrite `README.md` with end-to-end onboarding, expanded installation steps for `uv`,
  new quick-start command walkthroughs, and refreshed status badges.
- Polish `AGENTS.md`, user recipes, quickstart, and command references to align terminology with JSON-lines streaming,
  add richer examples, and clarify polling presets.
- Consolidate best-practices guidance into `docs/users/best_practices.md`, removing the obsolete duplicate file.
- Add a maintenance check reminder to `docs/developers/architecture.md`.

## [0.1.0] - 2025-10-17

### Added

- Provide structured Research SSE parsing in client: `research_stream_events()` returns `{event, data}` objects.
- CLI `research stream` emits one JSON object per event (JSON-lines).
- CLI `answer --stream` streams answer chunks via SDK.
- Context transport improvements:
  - Enable HTTP/2 for the Context HTTP client.
  - Apply minimal exponential backoff on transient errors (RequestError, HTTP 5xx): 0.1s, 0.2s, 0.5s, then final attempt.
- CI matrix runs on Python 3.11 (GIL) and 3.14 (free-threading) with a best‑effort print of `Py_GIL_DISABLED`.
- Unit tests for Context backoff (`tests/unit/test_context_backoff.py`).
- Project metadata: Python version classifiers for 3.10, 3.11, 3.14.
- Rich contents options across commands (mapped to SDK fields):
  - `--text`, `--text-max-characters`, `--text-include-html-tags`
  - `--highlights`, `--highlights-num-sentences`, `--highlights-per-url`, `--highlights-query`
  - `--summary-query`, `--summary-schema @file`
  - `--subpages`, `--subpage-target`
  - `--extras-links`, `--extras-image-links`
  - `--context`, `--context-max-characters`
  - `--livecrawl [always|preferred|fallback|never]`, `--livecrawl-timeout`
- CLI auto-switches to combined endpoints when contents options are present:
  - `search` → `search_and_contents`
  - `find-similar` → `find_similar_and_contents`
- Examples and templates:
  - `examples/stream_consumer.sh` (pretty-prints JSON-lines)
  - `examples/research_instructions.md`, `examples/research_schema.json`
  - `.env.example` with `EXA_API_KEY`
- Docs (developer-facing): `docs/developers/exa_py_api_reference.md` capturing canonical SDK surfaces.
- ADRs: `ADR-0011 httpx over requests`, `ADR-0012 final SDK surface`, `ADR-0013 typed JSON-lines streaming`.

### Changed

- Standardize research SDK usage: `research.create(...)`, `research.get(...)`, `research.list(...)`.
- Standardize contents to SDK: `get_contents(...)` replaces raw HTTP.
- Use SDK `stream_answer(...)` for client answer streaming.
- Extend CLI routing with contents option builder and answer streaming branch.
- Normalize docstrings to concise Google-style; keep minor line wraps for readability.
- Use httpx-only for CLI and error handling (remove `requests` from runtime CLI code).
- Align research params with the latest exa_py:
  - `research_get` calls `research.get(research_id, ...)` (no `task_id`).
  - `research_poll` relies on SDK defaults via `poll_until_finished(research_id)`.
  - Remove unsupported `--infer-schema` flag and corresponding service arg.
  - Keep `--preset` as a convenience hint; polling behavior remains SDK-default.
  - Switch research streaming to SDK typed events; CLI emits JSON-lines only.
  - Add `answer --stream --json-lines` for agent-friendly chunk events.
  - Use `httpx.Client` for `/context` endpoint; enable HTTP/2 and timeout with unified error handling.

### Fixed

- Retain research endpoint correctness and headers for SSE; retry connections on
  initial SSE connect for transient statuses (429/502/503/504).
- Tests cover SDK-first research get, streaming JSON-lines, and `answer --stream`.
- Update tests for SDK-aligned research calls and simplified polling defaults.

### Removed

- Remove legacy research fallbacks and compatibility shims:
  - Remove `create_task`/`get_task`/`list_tasks` probing; rely on the final SDK interface.
  - Remove HTTP fallback for `research_get`.
- Remove unnecessary `_sleep` wrapper.

### CI / Tooling / Dependencies

- Enforce `exa_py>=1.16.1,<2.0` and `httpx>=0.27,<1.0`.
- Ruff, Pyright, Pylint (≥9.5), Pytest wired in CI.
- Add Python version classifiers; `requires-python = ">=3.10"`.

### Documentation

- README: Research 2.0 quickstart; inline contents with search; rich contents options; streaming answers.
- AGENTS.md: Expanded agent routing to include rich contents options and `answer --stream`.
- README/Quickstart: Transport notes for Context client (HTTP/2, timeout, short backoff).
