# ADR-0018: Introduce Workflow Registry Layer

**Date:** 2025-10-20  
**Status:** Approved  
**Drivers:** Unify orchestration, avoid duplicated CLI/service glue, expose shared schemas for external integrations.

## Decision

Create a lightweight workflow registry under `src/exa_direct/workflows/` with:

- Pydantic v2 models (`WorkflowInputs`, `WorkflowOutputs`) for validation and JSON Schema export.
- Step helpers that invoke existing `ExaService` and `httpx` calls directly (no additional wrappers).
- A registry API to register built-in workflows (`research_run`, `context_build`, `monitor_keyword`) and expose
  metadata for CLI/Responses/Agents surfaces.
- Optional plan generation (`--dry-run`/`--plan`) returning ordered step descriptions without executing them.

## Rationale

- Provides a single source of truth for orchestration shared across CLI, Codex CLI, Responses, and Agents surfaces.
- Keeps the layer simple—no custom DSL, only structured sequencing and post-processing—minimizing maintenance.
- Enables schema export for external integrations (`model_json_schema`, `TypeAdapter.json_schema`).

### Decision Framework Scoring

| Option | Solution Leverage | Application Value | Maintenance Load | Adaptability | Weighted |
| --- | --- | --- | --- | --- | --- |
| **Central registry (FINAL)** | 9.5 | 9.0 | 8.5 | 9.0 | **9.20** |
| Per-surface orchestration | 7.0 | 7.5 | 5.5 | 6.0 | 6.65 |
| Keep ad-hoc calls | 5.5 | 6.0 | 6.0 | 5.0 | 5.80 |

## Consequences

- New package `src/exa_direct/workflows/` with `base.py`, `steps.py`, `registry.py`, and `builtins.py`.
- CLI refactor to route existing commands through single-step workflows while exposing new composite commands.
- Responses/Agents integrations can resolve workflows by name and reuse schemas/logic without additional wrappers.
- Testing must cover workflow validation, plan output, and concurrency helpers.

## Alternatives Considered

- Maintain separate orchestration layers per surface (CLI, Responses, Agents) with duplicated logic.
- Keep direct `ExaService` calls in each command/tool and generate JSON schemas on demand.

## Implementation Notes

- Registry lives in `src/exa_direct/workflows/registry.py`; importing `exa_direct.workflows` auto-registers built-ins.
- Inputs/outputs are Pydantic v2 models to enable validation and schema export.
- Workflow execution emits `workflow.start`/`workflow.succeeded` via `structured_logging`.

## References

- docs/plans/2025-10-20-comprehensive-plan.md
- src/exa_direct/workflows/base.py
- src/exa_direct/workflows/builtins.py
