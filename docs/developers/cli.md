# CLI Surface

This page summarizes the command set exposed by `exa_direct.cli` and how each command maps to `ExaService`.

## Global Options

| Option | Behaviour |
| --- | --- |
| `--api-key` | Overrides `EXA_API_KEY`. If neither is provided, `client.resolve_api_key()` raises a `RuntimeError`. |
| `--pretty` | Pretty-prints JSON output only at the CLI layer; returned dictionaries stay unchanged. |
| `--save <path>` | Writes the final JSON payload to disk and still emits the same payload to stdout. |

`--pretty` and `--save` are evaluated after the command handler returns, so they apply uniformly to every command.

## Commands

| Command / Subcommand | Backend call(s) | Notes |
| --- | --- | --- |
| `search` | `ExaService.search` or `search_and_contents` | `--text`, `--highlights`, or other contents flags trigger `search_and_contents`. |
| `contents` | `ExaService.contents` | Accepts one or more URLs and forwards option flags verbatim. |
| `find-similar` | `ExaService.find_similar` or `find_similar_and_contents` | Uses `find_similar_and_contents` when any contents flag is present. |
| `answer` | `ExaService.answer`, `answer_stream`, `answer_stream_json` | Streaming is enabled by `--stream`; JSON-lines via `--stream --json-lines`. |
| `research start` | `ExaService.research_start` | Reads `--instructions` and `--schema` from inline values or `@file` references. |
| `research get` | `ExaService.research_get` | Supports `--events` to request event history. |
| `research list` | `ExaService.research_list` | Passes through pagination flags. |
| `research poll` | `ExaService.research_poll` | Blocks until completion using SDK defaults. |
| `research stream` | `ExaService.research_stream` | Emits JSON lines (UTF-8) to stdout. |
| `context query` | `ExaService.context` (HTTP POST) | Uses the shared `httpx.Client` managed by `ExaService`. |
| `workflow list` | `workflows.registry.list()` | Returns name/summary pairs. |
| `workflow describe` | `workflows.registry.get()` | Includes optional JSON schemas and static plan entries. |
| `workflow run` | `workflows.registry.execute()` | Accepts inline `--param key=value` pairs or `--input @file.json`; `--plan` skips execution. |

Every handler delegates directly to the workflow registry so documentation here stays in sync with the workflow layer.

## Streaming Behaviour

- `answer --stream` writes chunks directly to stdout. Use `--json-lines` to receive structured events.
- `research stream` always produces JSON lines; consumers should parse per line.
- Other commands return a single JSON object.

## Configuration Precedence

Current precedence for configuration inputs:

1. CLI flag (`--api-key`, etc.).
2. Environment variable (`EXA_API_KEY`).
3. No configuration files or defaults beyond those baked into the CLI are currently supported.

Future configuration files must sit below CLI flags and environment variables to avoid breaking automation. No hidden
state is stored across runs; workflows operate solely on provided parameters and inline JSON payloads.
