# Best Practices

This guide summarizes field‑tested guidance for using the Exa API via the `exa` CLI.
It is distilled from deep research completed on 2025‑10‑16 and validated by our internal usage.

## Search Types

- **auto**: balanced default for mixed queries.
- **fast**: latency‑optimized; ideal for iterative agent loops.
- **neural**: semantic exploration; concept‑heavy queries.
- **keyword**: exact matching; proper nouns and literal phrases.

Tip: Start with `fast` for interactive flows; switch to `auto`/`neural` when recall matters more than latency.

## Contents Retrieval

- `--highlights`: skim‑friendly, small payloads.
- `--text`: full page text for LLM ingestion.

Prefer highlights for triage; fetch text only for selected URLs that require deeper analysis.

## Livecrawling Modes

- `preferred` (recommended): attempt live, fallback to cache.
- `always`: strict freshness; expect occasional timeouts/failures.
- `fallback` or `never`: speed/cost bias or historical snapshots.

For large batches, reduce livecrawl timeouts in cURL workflows to maintain responsiveness.

## Answer vs. Research

- **answer**: synchronous Q&A with citations; fastest path; unstructured output.
- **research**: asynchronous multi‑step reasoning with optional JSON Schema output; poll or stream.

Schema guidance: keep ≤10 root fields, shallow nesting (≤2), and add `description` per field. Split oversized tasks.

## Research Operations

- Model pick: `exa-research-fast` (<~30 s), `exa-research` (1–2 min), `exa-research-pro` (>2 min).
- Polling presets: `fast=10s`, `exa-research=30s`, `pro=40s`; override via `--interval` when needed.
- Streaming: `exa research stream` prints event lines; use `--json-events` to emit JSON per event.

## Context (Exa Code)

Use `--tokensNum dynamic` by default; increase (e.g., 2048+) when the agent needs broader snippet windows.

## Pitfalls and Mitigations

- Missing API key → set `EXA_API_KEY` or pass `--api-key`.
- Large payloads → prefer highlights, batch fewer URLs, reduce livecrawl.
- Ambiguous prompts → clarify instructions and provide schemas/examples.
- Polling overhead → use `stream` or increase `--interval`.

## Example Sequences

- Discover + triage: `search --type fast --pretty` → shortlist → `contents --highlights`.
- Structured report: `research start --model exa-research --schema @schema.json` → `poll` or `stream`.
- Code examples: `context query --query "<library topic>" --tokensNum dynamic`.
