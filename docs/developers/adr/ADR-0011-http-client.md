# ADR-0011: HTTP Client Selection (httpx over requests)

Date: 2025-10-17  
Status: Accepted

## Context

The CLI makes a direct HTTP call to the `/context` endpoint (not wrapped by `exa_py`). Historically it used `requests`.
The `exa_py` SDK uses `httpx` in async paths. We want consistency, performance, and a single modern client.

## Decision

Use `httpx.Client` for non-SDK HTTP calls.

## Rationale (Decision Framework)

- Solution Leverage (35%): 0.34 — aligns with `exa_py` ecosystem; modern features; good docs.  
- Application Value (30%): 0.27 — minor perf and better error modeling; consistent exceptions.  
- Maint. Load (25%): 0.24 — simple, small footprint change; fewer polyfills later.  
- Adaptability (10%): 0.09 — easier future migration to async if needed.  
- Weighted total: 0.94 (9.4/10) → adopt.

## Consequences

- Dependency changed to `httpx>=0.27,<1.0`.  
- CLI error handling updated to handle `httpx.HTTPStatusError` and `httpx.RequestError`.  
- Tests include a minimal `tests/httpx.py` stub to keep local runs hermetic.

## Alternatives Considered

- Keep `requests`: acceptable but less aligned; fewer async-friendly options.  
- aiohttp: heavier; no need for async end-to-end right now.
