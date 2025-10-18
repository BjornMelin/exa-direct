# ADR-0012: Finalize on SDK Surface (No Fallbacks)

Date: 2025-10-17  
Status: Accepted

## Context

Earlier versions used getattr checks and alternate names (`task_id`, `create_task`) to cope with drift.
This increased complexity and risk.

## Decision

Remove all fallbacks and call only the final SDK surface:

- `research.create(...)`, `research.get(research_id, ...)`, `research.list(...)`, `poll_until_finished(research_id, ...)`.
- `search`, `search_and_contents`, `get_contents`, `find_similar`, `find_similar_and_contents`, `answer`, `stream_answer`.

## Rationale (Decision Framework)

- Solution Leverage (35%): 0.35 — uses maintained SDK; fewer local branches.  
- Application Value (30%): 0.30 — correctness; fewer runtime surprises.  
- Maint. Load (25%): 0.25 — simpler code; tighter tests.  
- Adaptability (10%): 0.10 — future changes are caught in tests.  
- Weighted total: 1.00 (10/10) → adopt.

## Consequences

- Immediate failure if SDK changes; mitigated by tests and release checklist.  
- Users get consistent, documented behavior.

## Alternatives Considered

- Keep fallbacks/feature flags: rejected (violates FINAL-ONLY rule, increases drift).
