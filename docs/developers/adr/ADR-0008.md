# ADR-0008: Quality Gates (ruff, pylint, pyright, pytest)

**Date:** 2025-10-16  
**Status:** Accepted  
**Drivers:** Code health, clarity, maintainability.

## Context

We need consistent formatting, linting, typing, and tests with low friction.

## Decision

Adopt ruff format+lint, pyright (basic), pylint with `--fail-under=9.5`, pytest.

### Decision Framework Scoring

| Option                       | Coverage | Latency | Ergonomics | Invocability | Maintenance | Extensibility | Weighted |
|------------------------------|----------|---------|------------|--------------|-------------|---------------|----------|
| **ruff+pylint+pyright+pytest** | 10     | 10      | 9          | 9            | 9           | 9             | 9.50     |
| Formatter-only               | 7        | 10      | 10         | 10           | 8           | 8             | 8.70     |

## Consequences

Consistent quality; small overhead.

## Alternatives Considered

Formatter-only.

## Implementation Notes

See `pyproject.toml` for tool settings.

## References

N/A
