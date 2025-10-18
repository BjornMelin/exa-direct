# Best Practices

Field‑tested guidance for using the Exa API via the `exa` CLI.

## Search Types

- auto (balanced)
- fast (latency‑optimized)
- neural (semantic)
- keyword (exact)

## Contents Retrieval

- Use `--highlights` to triage.
- Add `--text` only when full content is required.

## Livecrawling

- `preferred` by default.
- `always` for strict freshness.
- `fallback`/`never` for speed or static content.

## Answer vs. Research

- `answer` for synchronous Q&A with citations.
- `research` for structured, multi‑step tasks using a schema.

## Research Models & Polling

- Presets: fast=10s, balanced=30s, pro=40s (CLI UX guidance).
- Prefer `exa research stream` for real-time updates.
- `exa research poll` uses SDK defaults; set `--interval` or wrapper timeouts when you need the CLI presets.

## Context (Exa Code)

- Start with `--tokensNum dynamic`.
- Increase tokens when broader snippet windows are required.
