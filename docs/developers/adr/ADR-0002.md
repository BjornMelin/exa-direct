# ADR-0002: Python-First CLI vs TypeScript or cURL-only

**Date:** 2025-10-16  
**Status:** Accepted  
**Drivers:** Fast implementation, ergonomics, tests, minimal deps.

## Context

We need a CLI that is easy to call from shell/CI and simple to extend/test.

## Decision

Python CLI using `exa_py` and argparse; include cURL helpers. Defer TS until needed.

### Decision Framework Scoring

| Option             | Coverage | Latency | Ergonomics | Invocability | Maintenance | Extensibility | Weighted |
|--------------------|----------|---------|------------|--------------|-------------|---------------|----------|
| **Python (FINAL)** | 10       | 8.5     | 10         | 9            | 9           | 9             | 9.25     |
| TypeScript         | 9        | 8.5     | 7          | 7            | 7           | 9             | ~9.00    |
| cURL-only          | 8        | 9       | 6          | 8            | 7           | 8             | 7.70     |

## Consequences

Python ensures strong SDK support and tests; TS optional later.

## Alternatives Considered

TS-first; cURL-only.

## Implementation Notes

argparse + `exa_py`; cURL in `scripts/exa.sh`.

## References

- https://docs.exa.ai/sdks/python-sdk-specification
