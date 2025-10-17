# ADR-0005: Research Polling Intervals by Model

**Date:** 2025-10-16  
**Status:** Accepted  
**Drivers:** Predictable UX; different model runtimes.

## Context

Models differ in typical completion times; a single fixed interval is suboptimal.

## Decision

Presets: `exa-research-fast` 10s; `exa-research` 30s; `exa-research-pro` 40s; override via `--interval`.

### Decision Framework Scoring

| Option                     | Coverage | Latency | Ergonomics | Invocability | Maintenance | Extensibility | Weighted |
|----------------------------|----------|---------|------------|--------------|-------------|---------------|----------|
| **Presets + override**     | 10       | 9       | 9          | 9            | 10          | 9             | 9.40     |
| Single fixed interval      | 10       | 7       | 8          | 9            | 10          | 8             | 8.65     |

## Consequences

Faster convergence for fast/standard/pro tasks; consistent behavior.

## Alternatives Considered

Single 30s interval.

## Implementation Notes

CLI derives preset when `--interval` omitted.

## References

- https://docs.exa.ai/reference/research/create-a-task
- https://docs.exa.ai/reference/research/get-a-task
