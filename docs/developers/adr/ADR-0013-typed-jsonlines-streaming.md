# ADR-0013: Typed JSON-Lines Streaming for Research

Date: 2025-10-17  
Status: Accepted

## Context

Agents prefer newline-delimited JSON objects. The SDK emits typed Pydantic events when `stream=True`.

## Decision

Use SDK typed streaming and emit one JSON object per line. Remove raw SSE mode.

## Rationale (Decision Framework)

- Solution Leverage (35%): 0.35 — zero custom parsing; Pydantic models from SDK.  
- Application Value (30%): 0.30 — agent-friendly, robust framing.  
- Maint. Load (25%): 0.24 — less bespoke code; simpler docs.  
- Adaptability (10%): 0.10 — extendable with additional event fields.  
- Weighted total: 0.99 (9.9/10) → adopt.

## Consequences

- `exa research stream` prints NDJSON.  
- `answer --stream --json-lines` emits `{event:"chunk",data:"…"}` lines with a `done` sentinel.  
- Raw SSE output removed.

## Alternatives Considered

- Raw SSE with local parser: more brittle; discarded.
