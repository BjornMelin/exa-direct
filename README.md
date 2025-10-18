# exa-direct

[![CI](https://img.shields.io/github/actions/workflow/status/BjornMelin/exa-direct/ci.yml?branch=main&label=CI)](https://github.com/BjornMelin/exa-direct/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-index-blue)](./docs/index.md)
[![Python](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/)
[![API](https://img.shields.io/badge/API-Exa-blueviolet)](https://docs.exa.ai/reference/getting-started)

A focused CLI for direct Exa API usage (no MCP). It covers Search, Contents, Find Similar, Answer, Research
(Create/Get/List + Poll + Stream), and Context (Exa Code). It prints JSON by default, supports `--pretty`
and `--save`, and includes cURL helpers. LLM‑agnostic: integrate with OpenAI Agents SDK/Codex CLI or
Claude “tool use” (and LangGraph/LangChain) by invoking CLI commands and consuming JSON, no MCP server required.

It bootstraps quickly with `uv` (create a venv + `uv pip install -e .`), ships with research
polling/streaming helpers, and keeps options one-to-one with the official SDK so you always know which
flags Exa understands, and is easy to extend with new endpoints.

## Quick Start

1. **Install `uv` (skip if already installed)**
   - macOS/Linux:

     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```

   - Windows (PowerShell):

     ```powershell
     irm https://astral.sh/uv/install.ps1 | iex
     ```

2. **Create a virtual environment and install exa-direct**

   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e .
   ```

3. **Provide your API key**

   ```bash
   export EXA_API_KEY=sk-...
   ```

4. **Run your first query**

   ```bash
   exa search --query "state of AGI" --type fast --pretty
   ```

Want structured research or code-aware context? Swap the final command for `exa research stream ...` or
`exa context query ...`—the flags mirror the SDK and every command prints JSON for downstream tooling.

### Why agents call the CLI directly

- **Codex & Claude Code CLI friendly:** Designed for OpenAI Codex CLI and Claude Code CLI sessions to execute
  commands directly instead of routing through the Exa MCP server.
- **Lower latency & tighter control:** Avoid MCP indirection to keep roundtrips fast, tighten search/research
  loops, and stream incremental output straight into your agent workflow.
- **Full Exa surface:** Unlock extended Exa API capabilities (live crawl policies, schema-driven summaries,
  context payloads, cURL helpers) that the MCP server cannot reach, plus the `exa-research-fast` model not
  available via MCP tooling.
- **Future-ready:** When the SDK adds features, exa-direct gains them immediately because the CLI mirrors the
  underlying `exa_py` surface one-to-one.

## Features

- JSON to stdout; `--pretty` to format; `--save` to write files.
- Research streaming via JSON-lines and polling presets per model.
- Context (Exa Code) for code-focused results.
- Minimal dependencies: `exa_py`, `requests`.
- LLM‑agnostic: usable from OpenAI Agents SDK/Codex CLI, Claude “tool use”, LangGraph/LangChain by
  shelling out to this CLI and parsing JSON.

## Install

### 1. Install `uv`

- macOS/Linux:

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- Windows (PowerShell):

  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  ```

### 2. Set up the environment and install dependencies

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
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

- Research (stream JSON-lines):

```bash
exa research stream --id <researchId> | jq .
```

- Context:

```bash
exa context query --query "pandas groupby examples" --tokensNum dynamic
```

### Transport behavior (Context endpoint)

- HTTP/2 is enabled for the Context HTTP client to reduce latency.
- Requests use a total timeout; transient network errors and HTTP 5xx receive
  a short exponential backoff (0.1s, 0.2s, 0.5s) followed by a final attempt.

### Examples

See runnable scripts under `examples/`:

- `search_examples.sh`: search filters and inline contents
- `contents_examples.sh`: contents options (text/highlights/summary/metadata)
- `find_similar_examples.sh`: filters plus inline contents
- `answer_examples.sh`: structured and streaming answers (JSON-lines)
- `research_examples.sh`: start/poll/stream/get/list flows
- `context_example.sh`: Exa Code context queries

### Use with LLM Agents (no MCP)

- Trigger mode: call the CLI as a tool/command from your agent runtime, parse JSON from stdout, and optionally write
  large outputs via `--save`.
- Research guidance: prefer `exa research stream` for live progress or `exa research poll` with model‑aware intervals
- Keys: set `EXA_API_KEY` in the agent/container environment or pass `--api-key` per invocation.
- Safety & ops: validate/sanitize user input passed to the shell; restrict flags and apply timeouts; capture stderr
  for HTTP errors; consider retry with backoff on transient failures.
- Streaming: `exa research stream` emits JSON-lines (one object per line) using typed SDK events. If your framework
  cannot stream, switch to polling and print the final JSON on completion.

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
    exa research poll --id <researchId> --preset balanced --pretty
    ```

3) Or stream events as JSON-lines:

    ```bash
    exa research stream --id <researchId> | jq .
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

See [CHANGELOG](CHANGELOG.md) for release notes (latest: v0.1.0).

### Examples

- Python agent helpers: `examples/agents_python.py`
- Pipeline (search → contents → answer): `examples/pipeline_search_contents_answer.py`
- Research streaming (JSON-lines): `examples/research_stream_json.py`
- Context for RAG prompts: `examples/context_rag_snippet.py`

## Development

### Quality gates

```bash
uv run ruff format
uv run ruff check . --fix
uv run pyright
uv run pylint --fail-under=9.5 src/exa_direct tests
uv run python -m pytest -q
```

### Git hooks and CI

- Enable the repo’s pre-commit hook (formats with ruff, lints Markdown, and re-stages fixes):

```bash
git config core.hooksPath scripts/git-hooks
```

- CI runs markdownlint on PRs via `.github/workflows/markdownlint.yml`.
- CI runs Ruff format/lint via `.github/workflows/ruff.yml`.

### cURL Helpers

- `scripts/exa.sh` provides functions:
  - `exa_search`: Fast search with text.
  - `exa_contents`: Contents (livecrawl preferred).
  - `exa_find_similar`: Find similar links.
  - `exa_answer`: Answer with citations.
  - `exa_context`: Context (Exa Code).
  - `exa_research_start`: Research (create + poll).
  - `exa_research_get`: Research (get).
  - `exa_research_stream`: Research (stream JSON-lines).
  - `exa_research_list`: Research (list).

### References

- **Exa overview:** <https://exa.ai/blog/exa-api-2-0>
- **Endpoints:**
  - **Search:** <https://docs.exa.ai/reference/search>
  - **Contents:** <https://docs.exa.ai/reference/get-contents>
  - **Find Similar:** <https://docs.exa.ai/reference/find-similar-links>
  - **Answer:** <https://docs.exa.ai/reference/answer>
  - **Research:**
    - **Create:** <https://docs.exa.ai/reference/research/create-a-task>
    - **Get:** <https://docs.exa.ai/reference/research/get-a-task>
    - **List:** <https://docs.exa.ai/reference/research/list-tasks>
  - **Context:** <https://docs.exa.ai/reference/context>
  - **How Exa Search Works:** <https://docs.exa.ai/reference/how-exa-search-works>
  - **Livecrawling Contents:** <https://docs.exa.ai/reference/livecrawling-contents>

## Agents SDK examples (Python/JS)

Python (shell out from an agent/tool)

```python
import json
import os
import subprocess
from typing import Any, Sequence


def run_exa(args: Sequence[str]) -> dict[str, Any]:
    env = {**os.environ, "EXA_API_KEY": os.environ.get("EXA_API_KEY", "")}
    proc = subprocess.run(
        ["exa", *args],
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(proc.stdout)


def exa_search(query: str, type_: str = "fast") -> dict[str, Any]:
    return run_exa(["search", "--query", query, "--type", type_])


def exa_research(query_path: str, schema_path: str, model: str = "exa-research") -> dict[str, Any]:
    start = run_exa([
        "research", "start",
        "--instructions", f"@{query_path}",
        "--schema", f"@{schema_path}",
        "--model", model,
    ])
    task_id = start.get("id") or start.get("taskId")  # SDK/REST variants
    assert task_id, f"No task id in: {start}"
    # Poll with model-aware default (override with --interval if needed)
    return run_exa(["research", "poll", "--id", task_id, "--model", model])


if __name__ == "__main__":
    os.environ.setdefault("EXA_API_KEY", "sk-...set-me...")
    print(exa_search("hybrid search vector databases"))
```

### Notes

- Escape or validate any user-provided strings passed to the shell.
- For large outputs, add `--save /path/out.json` and read the file from your agent.
- For real-time UX, prefer `exa research stream` where your framework supports streaming; otherwise poll.

### Inline contents with search

```bash
# Return search results with text, highlights, and a short summary
exa search --query "state of AGI" --text --highlights --summary-query "key points" --pretty

# Advanced: constrain text length and include HTML tags; crawl subpages
exa search --query "state of AGI" \
  --text --text-max-characters 2000 --text-include-html-tags \
  --highlights --highlights-num-sentences 2 --highlights-per-url 2 \
  --summary-query "main developments" \
  --subpages 1 --subpage-target sources \
  --extras-links 2 --extras-image-links 1 \
  --livecrawl preferred --livecrawl-timeout 1000 --pretty
```

### Contents (rich options)

```bash
# Full text + highlights + summary (schema)
exa contents https://arxiv.org/abs/2307.06435 \
  --text --highlights --summary-schema @examples/research_schema.json --pretty
```

### Find similar (with contents)

```bash
exa find-similar --url https://example.com --text --highlights --pretty
```

### Streaming answers

```bash
exa answer --query "What is the latest valuation of SpaceX?" --stream
```
