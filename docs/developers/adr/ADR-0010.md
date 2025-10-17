# ADR-0010: Documentation Set and Style

**Date:** 2025-10-16  
**Status:** Accepted  
**Drivers:** Onboarding speed; reproducibility; explicit references.

## Context

We need user and developer docs, a PRD, and ADRs to track decisions.

## Decision

Maintain docs under `docs/` with user/developers subtrees; PRD at `docs/prd.md`; ADRs in `docs/developers/adr`.

### Decision Framework Scoring

| Option                    | Coverage | Latency | Ergonomics | Invocability | Maintenance | Extensibility | Weighted |
|---------------------------|----------|---------|------------|--------------|-------------|---------------|----------|
| **Separate user/dev docs**| 10       | 10      | 9          | 10           | 9           | 9             | 9.65     |

## Consequences

Clear separation; quick onboarding; explicit references.

## Alternatives Considered

README-only.

## Implementation Notes

Index at `docs/index.md`; cross-links to Exa official docs.

## References

All links listed in ADR-0001.
