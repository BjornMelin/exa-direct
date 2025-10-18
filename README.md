# exa-direct

[![CI](https://img.shields.io/github/actions/workflow/status/BjornMelin/exa-direct/ci.yml?branch=main&label=CI)](https://github.com/BjornMelin/exa-direct/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-index-blue)](./docs/index.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![API](https://img.shields.io/badge/API-Exa-blueviolet)](https://docs.exa.ai/reference/getting-started)

**Neural Search • Web Scraping • Live Crawling • Research Synthesis • Code
Context—complete Exa API access via CLI for AI agents, zero MCP overhead.**

Your Codex CLI, Claude Code CLI, or Gemini CLI agents shell out to `exa`
commands and parse JSON. No MCP server setup, no protocol negotiation—just
`subprocess.run(["exa", ...])` and you're scraping, searching, and researching.
Install with `uv` in seconds, export your key, and let your agents call Exa
directly.

## Install

### 1. Install `uv`

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### 2. Set up environment

```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .
```

### 3. Configure API key

```bash
export EXA_API_KEY=sk-...  # Windows: $env:EXA_API_KEY="sk-..."
```

## Why Use This Instead of MCP?

**For AI agent developers:** When your Codex CLI, Claude Code CLI, or custom
agents need Exa capabilities, subprocess calls beat MCP servers:

- **Zero infrastructure:** No MCP server process, no port management—just
  `exa search --query "..." --pretty`
- **Lower latency:** Direct SDK calls eliminate server round trips; HTTP/2 for
  Context API; exponential backoff (0.1s → 0.2s → 0.5s) handles failures
- **Complete API surface:** All six search types, three research models
  including `exa-research-fast`, livecrawl policies, schema-driven outputs—MCP
  can't access everything
- **Easier debugging:** `exa` commands run standalone; test in terminal, paste
  into agent workflows; `--pretty` for inspection, `--save` for large outputs

## Quick Start

Once installed and configured (see Install section above), try these commands:

```bash
# Neural search with inline content scraping
exa search --query "AGI breakthroughs 2025" --type fast --text --pretty

# Scrape fresh web content
exa contents https://example.com --text --livecrawl preferred --pretty

# Get code context for RAG
exa context query --query "FastAPI async patterns" --tokensNum dynamic --pretty
```

## Core Commands

### Neural & Keyword Search

Six search types (auto, neural, keyword, fast, hybrid, deep) for semantic and literal discovery:

```bash
# Fast neural search with inline page scraping
exa search --query "LLM agent frameworks" --type fast --text --num-results 5

# Hybrid search with domain filters
exa search --query "vector databases" --type hybrid \
  --include-domains qdrant.tech pinecone.io --text --pretty

# Advanced: full content with highlights and summaries
exa search --query "state of AGI" --text --highlights \
  --summary-query "key developments" --livecrawl preferred --pretty
```

**Perfect for agents:**

- Use `--text` to get page content directly, or combine with `--highlights` for quick triage.
- Add `--summary-query` for AI-generated summaries and `--livecrawl preferred` for fresh content.
- Every result includes metadata for filtering and ranking.

### Web Scraping

Fresh vs cached content policies (always, preferred, fallback, never, auto) for current vs historical data:

```bash
# Scrape with livecrawl for up-to-date content
exa contents https://docs.python.org/3/whatsnew/ \
  --text --highlights --livecrawl preferred --pretty

# Batch scrape with summaries
exa contents https://site1.com https://site2.com \
  --text --summary-query "key points" --livecrawl always

# Advanced: rich content with subpages and metadata
exa contents https://example.com --text --highlights --summary-query "overview" \
  --subpages 2 --extras-links 3 --livecrawl preferred --livecrawl-timeout 2000
```

**Fresh content for agents:**

- Use `preferred` for production-safe freshness with fallbacks, or `always` when you need current data.
- Add `--summary-query` for AI-generated summaries, `--subpages` to crawl linked pages,
  `--extras-links` for additional URLs, and `--extras-image-links` for image URLs.
- Set `--livecrawl-timeout` to control crawl speed.

### Research Synthesis

Three models: `exa-research-fast` (speed), `exa-research` (balance),
`exa-research-pro` (depth) for structured multi-source analysis:

```bash
# Start research with structured schema
exa research start \
  --instructions @examples/research_instructions.md \
  --schema @examples/research_schema.json \
  --model exa-research-fast

# Stream JSON-lines events (chunk, result, error)
exa research stream --id <taskId> | jq .

# Or poll until complete
exa research poll --id <taskId> --pretty
```

**Structured research for agents:**

- Want JSON output with custom schemas? Use `research stream` for real-time results or `research poll` for batched completion.
- Every command mirrors the SDK—flags work identically, JSON output ready for downstream tooling.

### Code Context for RAG

Dynamic or fixed token budgets (1K–50K) for code-aware search results:

```bash
# Dynamic token budget (adapts to query)
exa context query --query "React useEffect cleanup" --tokensNum dynamic

# Fixed token limit
exa context query --query "pandas DataFrame joins" --tokensNum 5000 --pretty
```

**Code-aware RAG:**

- Perfect for retrieving relevant code examples, documentation, and patterns.
- Use `dynamic` for adaptive context windows or set fixed limits for consistent token usage across queries.

### Find Similar & Answer

Discover related content and get AI-powered answers with citations:

```bash
# Find similar pages with inline scraping
exa find-similar --url https://arxiv.org/abs/2307.06435 \
  --num-results 5 --text --pretty

# AI-generated answer
exa answer --query "What changed in Exa 2.0?" --pretty

# Stream answer
exa answer --query "Latest AI developments" --stream
```

**Content discovery for agents:**

- Start with a known good URL and find similar pages, or ask questions to get AI-generated answers with source citations.
- Perfect for expanding your knowledge base or answering user queries.

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

## Use Cases

**Research Agent:** Multi-source synthesis with structured output

```bash
exa research start --instructions "@query.txt" --model exa-research-fast
exa research stream --id <taskId> | jq -r '.data.answer // empty'
```

**RAG Pipeline:** Code context retrieval

```bash
exa context query --query "Django async views" --tokensNum dynamic --save /tmp/ctx.json
```

**Fresh Web Data:** Latest docs with livecrawl

```bash
exa contents https://docs.example.com/latest \
  --text --livecrawl always --summary-query "what's new"
```

## Features

- **Six search types** for semantic and keyword discovery
- **Livecrawl policies** for fresh vs cached content
- **Research synthesis** with typed streaming (Pydantic-validated JSON-lines)
- **Code context** with dynamic or fixed token budgets (1K–50K)
- **Combined operations** (`search_and_contents`, `find_similar_and_contents`)
  reduce round trips
- **Agent-optimized:** JSON stdout, `--pretty`/`--save` flags, `@file` syntax
- **Automatic resilience:** HTTP/2, exponential backoff, retry logic

## Examples & Documentation

**Examples:** `examples/` directory contains working scripts:

- `agents_python.py` - Drop-in Python helpers
- `*.sh` - Shell scripts for all endpoints
- `pipeline_search_contents_answer.py` - Multi-step workflow
- `research_stream_json.py` - Research streaming
- `context_rag_snippet.py` - RAG integration

**Documentation:** See [docs/index.md](docs/index.md) for:

- [Quickstart](docs/users/quickstart.md) - Getting started
- [Commands](docs/users/commands.md) - CLI reference
- [Best Practices](docs/users/best_practices.md) - Agent integration patterns
- [Architecture](docs/developers/architecture.md) - Implementation details

**Changelog:** [CHANGELOG.md](CHANGELOG.md) - Release notes (latest: v0.1.0)

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

## Agent Integration

### Python (Codex CLI, OpenAI Agents SDK)

#### Using subprocess to call the CLI

```python
import subprocess
import json

def run_exa(args: list[str]) -> dict:
    """Execute exa CLI command and return parsed JSON."""
    result = subprocess.run(
        ["exa"] + args,
        capture_output=True, text=True, check=True
    )
    return json.loads(result.stdout)

def exa_search(query: str, type_: str = "fast") -> dict:
    """Search with optional inline content fetching."""
    return run_exa(["search", "--query", query, "--type", type_, "--text"])

def exa_research(instructions_file: str, schema_file: str | None = None) -> dict:
    """Create and poll research task to completion."""
    args = [
        "research", "start",
        "--instructions", f"@{instructions_file}",
        "--model", "exa-research-fast"
    ]
    if schema_file:
        args.extend(["--schema", f"@{schema_file}"])

    start_result = run_exa(args)
    task_id = start_result.get("id") or start_result.get("taskId")
    if not task_id:
        raise ValueError(f"No task ID in response: {start_result}")

    return run_exa(["research", "poll", "--id", task_id])

# Use in agent
results = exa_search("AI agent frameworks comparison")
research = exa_research("query.md", "schema.json")
```

#### Using the Python client library directly

```python
from exa_direct import client

def exa_search_direct(query: str, type_: str = "fast") -> dict:
    """Search using the Python client directly."""
    service = client.create_service(client.resolve_api_key(None))
    return service.search(
        query=query,
        params={"type": type_, "num_results": 5}
    )

def exa_research_direct(instructions: str, schema: dict | None = None) -> dict:
    """Research using the Python client directly."""
    service = client.create_service(client.resolve_api_key(None))
    start_result = service.research_start(
        instructions=instructions,
        model="exa-research-fast",
        output_schema=schema
    )
    task_id = start_result["id"]
    return service.research_poll(research_id=task_id)

def exa_contents_direct(urls: list[str]) -> dict:
    """Fetch page contents with livecrawl."""
    service = client.create_service(client.resolve_api_key(None))
    return service.contents(
        urls=urls,
        text=True,
        highlights=True,
        livecrawl="preferred"
    )

# Use in agent
results = exa_search_direct("AI agent frameworks")
content = exa_contents_direct(["https://example.com"])
```

### Important Notes

- **Security:** Always escape or validate any user-provided strings passed to shell commands to prevent injection attacks.
- **Large outputs:** For large responses, use `--save /path/out.json` and read the
  saved file from your agent instead of parsing stdout.
- **Real-time vs batched:** Prefer `exa research stream` for real-time updates when your framework supports streaming;
  use `exa research poll` for batched completion.

### Shell (Claude Code CLI, Gemini CLI)

```bash
#!/bin/bash
# exa_tools.sh

exa_search() {
    exa search --query "$1" --type "${2:-fast}" --text --pretty
}

exa_research() {
    local task_json=$(exa research start \
        --instructions "@$1" \
        --schema "@$2" \
        --model "${3:-exa-research-fast}")

    local task_id=$(echo "$task_json" | jq -r '.id')
    exa research stream --id "$task_id" | jq .
}

# Usage: exa_search "vector databases"
# Usage: exa_research "query.md" "schema.json"
```

### TypeScript/JavaScript

```typescript
import { execSync } from 'child_process';

function exaSearch(query: string, type: string = 'fast'): any {
  const result = execSync(
    `exa search --query "${query}" --type ${type} --text`,
    { encoding: 'utf-8' }
  );
  return JSON.parse(result);
}

const results = exaSearch('AI agent frameworks');
```

## Advanced Usage

For power users who need fine-grained control over search, content extraction, and research parameters.

### Complex Search with Rich Content

```bash
# Deep Neural search with all content options
exa search --query "state of AGI" \
  --type neural --num-results 10 \
  --text --text-max-characters 3000 --text-include-html-tags \
  --highlights --highlights-num-sentences 3 --highlights-per-url 2 \
  --summary-query "key developments and trends" \
  --include-domains arxiv.org openai.com deepmind.com \
  --start-published-date 2024-01-01 \
  --livecrawl preferred --livecrawl-timeout 1500 \
  --pretty --save results.json
```

### Multi-Stage Content Processing

```bash
# Search with inline processing and subpage crawling
exa search --query "machine learning frameworks comparison" \
  --text --highlights --summary-query "framework comparison" \
  --subpages 2 --subpage-target related \
  --extras-links 5 --extras-image-links 2 \
  --livecrawl always --livecrawl-timeout 2000 \
  --num-results 5 --pretty
```

### Batch Processing with Filters

```bash
# Process multiple URLs with different content policies
exa contents \
  https://pytorch.org/docs/stable/index.html \
  https://tensorflow.org/guide \
  https://keras.io/getting_started \
  --text --text-max-characters 5000 \
  --highlights --highlights-num-sentences 2 \
  --summary-query "key features and capabilities" \
  --livecrawl preferred --livecrawl-timeout 1000 \
  --metadata --extras-links 3 \
  --pretty --save frameworks_analysis.json
```

### Research with Custom Schema and Streaming

```bash
# Advanced research with custom output schema and progress streaming
exa research start \
  --instructions @examples/research_analysis.md \
  --schema @examples/research_schema.json \
  --model exa-research-pro

# Monitor progress with streaming events
exa research stream --id <researchId> | jq -r '.data?.answer // .data?.chunk // empty'

# Get final results with full event history
exa research poll --id <researchId> --pretty --save final_report.json
```

### Context-Aware Code Search

```bash
# Advanced code context with specific constraints
exa context query --query "async database operations python" \
  --tokensNum 8000

# Multiple related queries for extensive context
for query in "asyncpg usage patterns" "sqlalchemy async best practices" "tortoise orm async"; do
  exa context query --query "$query" --tokensNum dynamic --save "context_${query// /_}.json"
done
```

### Agent Workflow: Search → Enrich → Research

```bash
#!/bin/bash
# Complete agent workflow combining multiple exa commands

TOPIC="autonomous AI agents"

# Phase 1: Discover and gather content
echo "🔍 Searching for content..."
SEARCH_RESULTS=$(exa search --query "$TOPIC" --type fast --text --highlights --num-results 15 --pretty)

# Phase 2: Deep dive on key sources
echo "📄 Extracting detailed content..."
KEY_URLS=$(echo "$SEARCH_RESULTS" | jq -r '.results[0:5].url')
exa contents $KEY_URLS --text --highlights --summary-query "key insights on $TOPIC" \
  --livecrawl preferred --livecrawl-timeout 1500 --save detailed_content.json

# Phase 3: Synthesize research analysis
echo "🧠 Researching research analysis..."
TASK_JSON=$(exa research start \
  --instructions @examples/agent_analysis.md \
  --schema @examples/agent_schema.json \
  --model exa-research)

TASK_ID=$(echo "$TASK_JSON" | jq -r '.id')
exa research poll --id $TASK_ID --pretty --save research_analysis.json

echo "✅ Analysis complete: research_analysis.json"
```

## API References

- [Search](https://docs.exa.ai/reference/search) - Search endpoint
- [Contents](https://docs.exa.ai/reference/get-contents) - Web scraping
- [Research](https://docs.exa.ai/reference/research/create-a-task) - Synthesis
- [Context](https://docs.exa.ai/reference/context) - Code context (Exa Code)
- [Find Similar](https://docs.exa.ai/reference/find-similar-links) - Similar pages
- [Answer](https://docs.exa.ai/reference/answer) - AI-generated answers
- [Livecrawl](https://docs.exa.ai/reference/livecrawling-contents) - Fresh content

---

**What's Next?**

- Structured research? `exa research stream --id <taskId>`
- Code examples? `exa context query --query "..." --tokensNum dynamic`
- Fresh web data? `exa contents <url> --livecrawl preferred --text`

Every command mirrors the Exa SDK, prints JSON, works standalone—test in your
terminal, drop into agent workflows.
