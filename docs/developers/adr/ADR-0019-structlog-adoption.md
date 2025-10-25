# ADR-0019: Adopt `structlog` for Structured Logging

**Date:** 2025-10-20  
**Status:** Approved  
**Drivers:** Consistent structured telemetry, minimal maintenance burden, shared context across CLI/agents.

## Decision

Use `structlog` as the primary logging facade with:

- Shared processors for timestamps, log levels, logger names, and structured exception info.
- Dev configuration (rich console renderer) and production configuration (JSON renderer) toggled via environment variables.
- Context propagation via `contextvars` (workflow IDs, request IDs, agent run IDs).
- Canonical workflow lifecycle events emitted from the workflow engine and CLI surfaces.
- Transparent bridging so stdlib loggers from dependencies continue to emit without changes.

## Rationale

- Provides higher solution leverage and observability than maintaining custom JSON adapters, while remaining lightweight.
- Supports per-environment renderers and canonical log lines for downstream aggregation.
- Simplifies correlation between CLI runs, Responses tool calls, and Agents SDK executions through shared context fields.

### Decision Framework Scoring

| Option | Solution Leverage | Application Value | Maintenance Load | Adaptability | Weighted |
| --- | --- | --- | --- | --- | --- |
| **structlog (FINAL)** | 9.0 | 8.5 | 8.0 | 8.5 | **8.65** |
| Stdlib logging + custom JSON | 7.0 | 7.5 | 6.5 | 7.0 | 7.15 |
| Third-party APM-specific logger | 6.0 | 6.5 | 5.5 | 6.0 | 6.10 |

## Consequences

- New `src/exa_direct/logging.py` module initializing structlog once at CLI startup.
- Canonical event emission in workflow engine to aid debugging and tracing.
- Tests must verify context propagation and JSON output shape.
- Documentation must describe logging behavior and configuration controls.

## Alternatives Considered

- Continue with stdlib logging plus custom JSON formatter and contextvar adapters.
- Integrate an APM-specific logger (e.g., OpenTelemetry exporter) for all telemetry needs.

## Implementation Notes

- Logging configuration lives in `src/exa_direct/structured_logging.py`.
- CLI entry point calls `structured_logging.configure()` before parsing arguments.
- Structured events include `workflow.start` / `workflow.succeeded` with contextvars-bound IDs.

## References

- docs/plans/2025-10-20-comprehensive-plan.md
- docs/logging.md
- src/exa_direct/structured_logging.py
