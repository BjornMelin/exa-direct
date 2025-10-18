# ADR-0004: Streaming Strategy (Typed SDK JSON-lines) With Polling Fallback

**Date:** 2025-10-16  
**Status:** Accepted  
**Drivers:** Real-time progress visibility without extra deps.

## Context

Research API supports typed streaming via the Python SDK (`research.get(..., stream=True)`).
Not all environments handle streaming reliably.

## Decision

Implement typed streaming via SDK; keep `poll` as fallback. Emit JSON-lines (one object per line) for agent compatibility.

### Decision Framework Scoring

| Option                           | Coverage | Latency | Ergonomics | Invocability | Maintenance | Extensibility | Weighted |
|----------------------------------|----------|---------|------------|--------------|-------------|---------------|----------|
| **SDK typed streaming (FINAL)**  | 10       | 9       | 9          | 9            | 9           | 9             | 9.30     |
| Poll only                        | 8        | 7       | 9          | 9            | 10          | 8             | 8.40     |
| SSE via third-party dependency   | 10       | 9       | 9          | 9            | 8           | 9             | 9.05     |

## Consequences

Minimal deps; explicit streaming path and reliable fallback.

## Alternatives Considered

Polling only; raw SSE via requests; sseclient dependency.

## Implementation Notes

Use SDK typed events; print one JSON object per line; `poll` relies on SDK defaults.

## References

- https://docs.exa.ai/reference/research/get-a-task
