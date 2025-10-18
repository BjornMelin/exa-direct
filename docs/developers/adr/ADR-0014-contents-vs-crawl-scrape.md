# ADR-0014 – Contents Command vs Split (Crawl + Scrape)

**Date:** 2025-10-18
**Status:** Accepted
**Decision:** Keep single `contents` command; do not split.

## Context

- **Authoritative sources:** `docs/developers/exa_py_api_reference.md`, `src/exa_direct/client.py`, `src/exa_direct/cli.py`.
- The Exa SDK `get_contents` surface supports both single-page and multi-page retrieval via:
  - `subpages: int` and `subpage_target: str | list[str]`
  - `livecrawl: {always|preferred|fallback|never}`, `livecrawl_timeout`
  - Payload shaping: `text`, `highlights`, `summary`, `extras`, `context`
- Current CLI exposes one `contents` command with flags that map onto these fields and are also
  reusable by `search` and `find-similar` when doing `*_and_contents`.

## Options Considered

**A)** Keep single `contents` (status quo), continue to expose both simple and advanced flags.
**B)** Replace with two commands:

- `scrape` for single-URL fetch with a minimal flag set
- `crawl` for multi-page/deep retrieval (subpages/subpage_target, livecrawl variants, etc.)

## Decision Framework Scoring (0–10, weights in parentheses)

- Solution Leverage (35%)
  - A: 9.0 – Directly leverages unified `get_contents` without duplication.
  - B: 8.5 – Same SDK surface, but split adds wrappers and surfaces duplication.
- Application Value (30%)
  - A: 8.5 – One mental model; advanced only when flags are used.
  - B: 8.2 – Clearer naming but modest gains (few advanced knobs today).
- Maint. & Cognitive Load (25%)
  - A: 9.5 – Single codepath/docs/tests.
  - B: 7.5 – Two commands to document, validate, and test.
- Architectural Adaptability (10%)
  - A: 9.0 – Add SDK options once; consistent across callers.
  - B: 8.5 – Could help if future deep traversal lands, but premature now.

**Weighted totals:**

- A: 8.975
- B: 8.16

**Gate:** Greenlight only if ≥ 9.0 → B does not meet threshold.

## Decision

Keep a single `contents` command. It already cleanly spans “single-page scraping” and “advanced crawling”
via `subpages`/`subpage_target` and `livecrawl` without user confusion when help text is clear.
Splitting would duplicate surfaces with limited user value.

## Rationale

- SDK surface is intentionally unified; mirroring that reduces drift and maintenance.
- Advanced controls are few; a dedicated `crawl` adds command sprawl with marginal benefit.
- Reuse of the same options across `search_and_contents` and `find_similar_and_contents` stays
  consistent when kept as one flag set.

## Consequences

- Users continue to use `exa contents <urls...>` and opt into deep retrieval by adding
  `--subpages` and `--subpage-target` as needed.
- Help text and validations must clearly communicate when advanced flags apply.

## Implementation Notes / Improvements (non-breaking)

- Validate and gate flags per SDK reference:
  - Remove or disable for `contents`: `--metadata`, `--filter-empty-results`, `--contents-flags`,
    and `--livecrawl auto`.
  - Keep them available only where supported (e.g., `search_and_contents`) after confirming
    SDK support, or drop entirely if not.
- Add validations:
  - If `--subpages` is provided without explicit `--subpage-target`, document default behavior
    (same-host discovery) or require target (decision in CLI docs + help text).
  - Enforce `--subpages >= 0`; `--livecrawl-timeout > 0`.
- Improve help UX:
  - Group flags into “Payload”, “Traversal”, “Freshness”, “Summarization”, “Context”.
  - Examples: single URL scrape; multi-URL batch; deep crawl with `subpages` and `preferred` livecrawl.
- Tests: add table-driven tests for `_build_contents_options` to assert exact SDK payloads passed to `ExaService.contents`.

## Alternatives Considered

- Introduce `scrape` as an alias to `contents` with a single-URL constraint. Rejected (adds
  duplication without new capability; violates FINAL-ONLY simplicity).

## Rollback Plan

If future SDK adds materially distinct deep-crawl features (e.g., traversal depth, sitemap
strategies, JS exec), revisit with a split. Until then, a single command remains optimal.

## References

- `docs/developers/exa_py_api_reference.md` (local, source-derived)
- `src/exa_direct/client.py`
- `src/exa_direct/cli.py`
