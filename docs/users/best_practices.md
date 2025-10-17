# Best Practices

Field‑tested guidance for using the Exa API via the `exa` CLI. See also `docs/user/best_practices.md`.

## Search Types

- auto (balanced), fast (latency), neural (semantic), keyword (exact).

## Contents Retrieval

- Use `--highlights` to triage; add `--text` only when full content is required.

## Livecrawling

- `preferred` default; `always` for strict freshness; `fallback/never` for speed/static.

## Answer vs Research

- `answer` for synchronous Q&A; `research` for structured, multi‑step tasks with schema.

## Research Models & Polling

- fast=10s, exa‑research=30s, pro=40s (override via `--interval`). Prefer `stream` for real‑time.

## Context (Exa Code)

- Start with `--tokensNum dynamic`; raise when broader snippet windows are needed.
