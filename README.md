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
  (fast=10s, balanced=30s, pro=40s). Set `--timeout` to bound runtime.
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

Node.js / TypeScript (child_process)

```ts
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const pexecFile = promisify(execFile);

async function runExa(args: string[]) {
  const { stdout } = await pexecFile("exa", args, {
    env: { ...process.env, EXA_API_KEY: process.env.EXA_API_KEY ?? "" },
    maxBuffer: 10 * 1024 * 1024,
  });
  return JSON.parse(stdout);
}

export async function exaSearch(query: string, type = "fast") {
  return runExa(["search", "--query", query, "--type", type]);
}

export async function exaResearch(
  instructionsPath: string,
  schemaPath: string,
  model = "exa-research"
) {
  const start = await runExa([
    "research", "start",
    "--instructions", `@${instructionsPath}`,
    "--schema", `@${schemaPath}`,
    "--model", model,
  ]);
  const id = (start as any).id ?? (start as any).taskId;
  if (!id) throw new Error(`No task id in ${JSON.stringify(start)}`);
  return runExa(["research", "poll", "--id", id, "--model", model, "--timeout", "900"]);
}

// Example usage
// process.env.EXA_API_KEY = "sk-...";
// const res = await exaSearch("hybrid search vector databases");
// console.log(res);
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
