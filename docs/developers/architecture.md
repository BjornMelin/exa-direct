# Architecture

## Goals

- Direct Exa API usage (no MCP) for Search, Contents, Find Similar, Answer,
  Research (Create/Get/List + Poll + Stream), and Context.
- Lightweight CLI with JSON stdout and minimal dependencies.

## Components

- `src/exa_direct/cli.py`: argparse-based command dispatcher; prints JSON; supports `@file` inputs.
- `src/exa_direct/client.py`: thin service layer using `exa_py` for all operations (typed stream for Research).
- `src/exa_direct/printing.py`: output helpers.
- `scripts/exa.sh`: cURL helper functions for quick shell usage.

## Data Flow

- CLI parses flags → constructs parameters → calls `ExaService` methods → prints JSON (and saves if requested).
- For Research stream: CLI emits JSON-lines using SDK typed events; polling uses SDK helper defaults.

## Maintenance Checks

- When Exa publishes Research REST updates, verify that the CLI's research streaming path still
  matches the official endpoints documented under Research below.

## Error Handling

- HTTP: status code and body emitted to stderr; exit code 1.
- Missing API key: explicit error with guidance to set `EXA_API_KEY`.
- File inputs: `@path` must exist and be UTF-8; schema must be valid JSON.

## Dependencies

- `exa_py` for supported methods (search, find_similar, answer, research helpers, etc.).
- `requests` for REST (Context endpoint). Research streaming uses the SDK.

## Non-Goals

- MCP server operation, policy gateways, or enterprise governance.
- Persistent storage, caching, or rate scheduling.

## Links

- **API 2.0:** <https://exa.ai/blog/exa-api-2-0>
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
