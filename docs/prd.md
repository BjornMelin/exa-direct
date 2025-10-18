# Product Requirements Document (PRD) – exa-direct

## 1. Summary

Build a standalone CLI to access Exa APIs directly (no MCP). Provide end-to-end tasks: Search, Contents, Find Similar,
Answer, Research (`create`, `get`, `list`, `poll`, `stream`), and Context (Exa Code). Keep usage simple, fast, and scriptable.

## 2. Goals

- Single binary entry (`exa`) for all supported endpoints.
- JSON output by default; pretty-print and save options.
- Research: support `exa-research-fast`, `exa-research`, `exa-research-pro`, polling defaults,
  typed streaming with JSON-lines (research stream).
- Context (Exa Code): enable code-focused context retrieval.

## 3. Non-Goals

- MCP server integration, gateways, enterprise governance, rate limiting, or caching.
- Web UI.

## 4. Users & Personas

- CLI-first developers; data/research engineers; CI pipelines generating reports.

## 5. Use Cases

- Fast search + contents to feed downstream processing.
- Single-shot Q&A with citations.
- Long-running research tasks with structured results (JSON Schema), observed via polling or streaming.
- Code-context retrieval for agents or developer prompts.

## 6. Functional Requirements

- Commands: `search`, `contents`, `find-similar`, `answer`, `research {start|get|list|poll|stream}`, `context query`.
- Flags: `--api-key`, `--pretty`, `--save`.
- File inputs: `@path` for instructions and schema.
- Exit codes: 0 success; non-zero for errors.

## 7. Non-Functional Requirements

- Latency: prefer `--type fast` where possible.
- Reliability: polling fallback to streaming.
- Observability: JSON outputs easily piped to logs/metrics (out-of-scope to add logging infra).
- Maintainability: minimal deps; ruff/pylint/pyright/pytest gates.

## 8. UX

- Consistent subcommands; help text; copy-pasteable examples in docs.

## 9. Milestones

- M0: Core endpoints (search/contents/find-similar/answer) – complete.
- M1: Research (start/get/list/poll/stream) – complete.
- M2: Context – complete.
- M3: Docs & examples – complete.

## 10. Risks & Mitigations

- API changes: track Exa docs; pin SDK; keep cURL examples current.
- Streaming variability: keep polling as fallback.

## 11. Metrics (Indicative)

- CLI latency P50 for common queries (local dev measurement).
- Adoption: number of commands run (manual; out-of-scope for telemetry).

## 12. References

- **Overview:** <https://exa.ai/blog/exa-api-2-0>
- **Endpoints:**
  - **Search:** <https://docs.exa.ai/reference/search>
  - **Contents:** <https://docs.exa.ai/reference/get-contents>
  - **Find Similar:** <https://docs.exa.ai/reference/find-similar-links>
  - **Answer:** <https://docs.exa.ai/reference/answer>
  - **Research:**
    - **Create:** <https://docs.exa.ai/reference/research/create-a-task>
    - **Get/Stream:** <https://docs.exa.ai/reference/research/get-a-task>
    - **List:** <https://docs.exa.ai/reference/research/list-tasks>
  - **Context:** <https://docs.exa.ai/reference/context>
  - **Livecrawling:** <https://docs.exa.ai/reference/livecrawling-contents>
