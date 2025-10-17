# exa-direct

[![Python](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/)
[![API](https://img.shields.io/badge/API-Exa-blueviolet)](https://docs.exa.ai/reference/getting-started)

A focused CLI for direct Exa API usage (no MCP). It covers Search, Contents, Find Similar, Answer, Research
(Create/Get/List + Poll + SSE), and Context (Exa Code). It prints JSON by default, supports `--pretty`
and `--save`, and includes cURL helpers. LLM‑agnostic: integrate with OpenAI Agents SDK/Codex CLI or
Claude “tool use” (and LangGraph/LangChain) by invoking CLI commands and consuming JSON—no MCP server required.

## Features

- JSON to stdout; `--pretty` to format; `--save` to write files.
- Research streaming via SSE and polling presets per model.
- Context (Exa Code) for code-focused results.
- Minimal dependencies: `exa_py`, `requests`.
- LLM‑agnostic: usable from OpenAI Agents SDK/Codex CLI, Claude “tool use”, LangGraph/LangChain by
  shelling out to this CLI and parsing JSON.

## Install

```bash
python -m venv .venv && . .venv/bin/activate
pip install -U pip
pip install -e .
```

## Configure

```bash
export EXA_API_KEY=sk-...
```

## Usage

- Fast search:

```bash
exa search --query "Latest research in LLMs" --type fast --pretty
```

- Research (create + poll):

```bash
exa research start --instructions @examples/research_instructions.md   --schema @examples/research_schema.json --model exa-research-fast
exa research poll --id <researchId> --model exa-research
```

- Research (stream SSE):

```bash
exa research stream --id <researchId>
```

- Research (stream JSON events):

```bash
exa research stream --id <researchId> --json-events | jq '. | {event, data}'
```

- Context:

```bash
exa context query --query "pandas groupby examples" --tokensNum dynamic
```

### Use with LLM Agents (no MCP)

- Trigger mode: call the CLI as a tool/command from your agent runtime, parse JSON from stdout, and optionally write
  large outputs via `--save`.
- Research guidance: prefer `exa research stream` for live progress or `exa research poll` with model‑aware intervals
  (fast=10s, balanced=30s, pro=40s). Set `--timeout` to bound runtime.
- Keys: set `EXA_API_KEY` in the agent/container environment or pass `--api-key` per invocation.
- Safety & ops: validate/sanitize user input passed to the shell; restrict flags and apply timeouts; capture stderr
  for HTTP errors; consider retry with backoff on transient failures.
- Streaming: SSE prints only event‑stream lines; if your framework cannot stream, switch to polling and print the
  final JSON on completion. Or use `--json-events` to emit one JSON object per event.

## Research 2.0 Quickstart

1) Create a task with schema (structured output):

    ```bash
    exa research start \
      --instructions @examples/research_instructions.md \
      --schema @examples/research_schema.json \
      --model exa-research
    ```

2) Poll until completion (preset interval based on model):

    ```bash
    exa research poll --id <researchId> --model exa-research --timeout 900 --pretty
    ```

3) Or stream events as JSON:

    ```bash
    exa research stream --id <researchId> --json-events | jq .
    ```

4) Retrieve events afterward:

    ```bash
    exa research get --id <researchId> --events --pretty
    ```

### Notes

- Models: `exa-research-fast` (quick), `exa-research` (balanced), `exa-research-pro` (deep).
- Prefer small, shallow JSON Schemas; add field descriptions for clarity.
- Back off on 429/5xx (the CLI/service handle basic retries).

## Documentation

See the [docs index](docs/index.md) for user and developer guides and ADRs.

## Development

### Quality gates

```bash
uv run ruff format
uv run ruff check . --fix
uv run pyright
uv run pylint --fail-under=9.5 src/exa_direct tests
uv run python -m pytest -q
```

### cURL Helpers

- `scripts/exa.sh` provides functions:
  - `exa_search`: Fast search with text.
  - `exa_contents`: Contents (livecrawl preferred).
  - `exa_find_similar`: Find similar links.
  - `exa_answer`: Answer with citations.
  - `exa_context`: Context (Exa Code).
  - `exa_research_start`: Research (create + poll).
  - `exa_research_get`: Research (get).
  - `exa_research_stream`: Research (stream SSE).
  - `exa_research_list`: Research (list).

### References

- **Exa overview:** <https://exa.ai/blog/exa-api-2-0>
- **Endpoints:** <https://docs.exa.ai/reference/search>, <https://docs.exa.ai/reference/get-contents>,
  <https://docs.exa.ai/reference/find-similar-links>, <https://docs.exa.ai/reference/answer>,
  <https://docs.exa.ai/reference/research/create-a-task>, <https://docs.exa.ai/reference/research/get-a-task>,
  <https://docs.exa.ai/reference/research/list-tasks>, <https://docs.exa.ai/reference/context>,
  <https://docs.exa.ai/reference/how-exa-search-works>, <https://docs.exa.ai/reference/livecrawling-contents>
