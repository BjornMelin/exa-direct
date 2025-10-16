# Architecture

## Goals
- Direct Exa API usage (no MCP) for Search, Contents, Find Similar, Answer, Research (Create/Get/List + Poll + SSE), and Context.
- Lightweight CLI with JSON stdout and minimal dependencies.

## Components
- `src/exa_direct/cli.py`: argparse-based command dispatcher; prints JSON; supports `@file` inputs.
- `src/exa_direct/client.py`: thin service layer using `exa_py` for convenience and `requests` for REST/SSE.
- `src/exa_direct/printing.py`: output helpers.
- `scripts/exa.sh`: cURL helper functions for quick shell usage.

## Data Flow
- CLI parses flags → constructs parameters → calls `ExaService` methods → prints JSON (and saves if requested).
- For Research SSE: CLI streams lines as received; polling uses SDK helper.

## Error Handling
- HTTP: status code and body emitted to stderr; exit code 1.
- Missing API key: explicit error with guidance to set `EXA_API_KEY`.
- File inputs: `@path` must exist and be UTF-8; schema must be valid JSON.

## Dependencies
- `exa_py` for supported methods (search, find_similar, answer, research helpers, etc.).
- `requests` for REST and streaming SSE.

## Non-Goals
- MCP server operation, policy gateways, or enterprise governance.
- Persistent storage, caching, or rate scheduling.

## Links
- API 2.0: https://exa.ai/blog/exa-api-2-0
- Search: https://docs.exa.ai/reference/search
- Contents: https://docs.exa.ai/reference/get-contents
- Find Similar: https://docs.exa.ai/reference/find-similar-links
- Answer: https://docs.exa.ai/reference/answer
- Research: https://docs.exa.ai/reference/research/create-a-task, https://docs.exa.ai/reference/research/get-a-task, https://docs.exa.ai/reference/research/list-tasks
- Context: https://docs.exa.ai/reference/context
- Livecrawling: https://docs.exa.ai/reference/livecrawling-contents
