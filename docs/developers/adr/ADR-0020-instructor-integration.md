# ADR-0020: Evaluate Instructor (python.useinstructor.com) for Typed Outputs

Date: 2025-10-19
Status: Rejected for now

## Context

- exa-direct v0.1.0 (Python 3.14+), SDK-first (`exa_py`).
- Deterministic outputs and optional structured outputs already exist:
  - Research: `exa_py.research` supports `output_schema` and Pydantic-typed results.
  - Answer: supports `--stream --json-lines` and `--output-schema` dict passthrough; no typed-model wrapper yet.
- Constraints: KISS/DRY/YAGNI, FINAL-ONLY, preserve existing JSON/NDJSON contracts and streaming.

## Options Considered

A) Answer typed mode with Instructor

- Inject Instructor to produce Pydantic-validated outputs for `exa answer`.
- Requires an additional LLM roundtrip (OpenAI/other) to parse Exa’s answer text, or replacing Exa Answer entirely.
- Breaks simplicity and adds latency/cost; streaming semantics complicate buffering and typed emission.

B) Macros-only validation with Instructor

- Use Instructor for post-processing (re-ask/validation) of research or custom macros.
- Duplicates `exa_py` typed support for research; introduces new dependency and keys; diverges from SDK-first.

C) No change (DX improvements only)

- Keep existing `output_schema` passthrough and streaming.
- Add CLI support for `--schema-py path:Class` to generate JSON Schema from local Pydantic v2 models and pass to Exa;
  optional local typed mapping at end of non-streamed calls.

## Decision Framework Scoring (Adopt threshold ≥ 9.0/10)

- Solution Leverage (35%): 6.0 → 2.10
- Application Value (30%): 6.5 → 1.95
- Maint. & Cognitive Load (25%): 5.0 → 1.25
- Architectural Adaptability (10%): 7.0 → 0.70
- Total: 6.0/10 → Below threshold. Reject.

## Rationale

- Instructor excels when the application directly calls model APIs (OpenAI Responses/Tools) with `response_model`
  and needs retries/validation/partials. exa-direct delegates `answer` to Exa's server, which already supports
  server-side schema enforcement and streaming; `research` already supports typed Pydantic outputs via SDK.
- Integrating Instructor would either be redundant (no effect in-line) or require a second LLM call, violating
  simplicity and increasing cost/latency.

## Accepted DX Scope (Final)

- Do not add Instructor dependency.
- Implement DX-only improvements that scored ≥ 9.0/10 (Decision Framework):
  - `--schema-py path:Class` flag for Answer and Research (convert Pydantic v2 model to JSON Schema and pass through
    existing `output_schema`).
  - `--typed-validate` (Answer, non-stream): validate final server JSON against provided model; fail fast on mismatch.
  - `--save-typed PATH`: persist validated typed object without changing stdout contracts.
  - Conflict checks and clearer CLI help for schema flags and invalid combinations.
  - Full tests (unit + integration + e2e shape) and user docs/examples.

## Deferred Items (to avoid overengineering)

- `--emit-final-typed` (streaming aggregation of a final typed object) — Deferred. Rationale: adds buffering/error
  paths with modest value; revisit only with demonstrated demand and stable framing guarantees.

## Revisit Criteria

Reconsider Instructor if any of the following become true:

- exa_py exposes a low-level Answer API that accepts/returns Pydantic types directly and benefits from local
  retry/validation hooks.
- We introduce local LLM calls (e.g., an offline answer mode) where Instructor provides clear leverage (≥9.0 DF score).
- User demand for robust re-asking/validation beyond server-side schemas grows, with acceptable latency/cost budgets.

Additionally, reconsider the deferred `--emit-final-typed` flag if multiple users/agents request an inline final
typed event for streams and we can aggregate safely without compromising streaming performance or memory bounds.

## Sources

- Instructor docs (features, streaming, retries): https://python.useinstructor.com/
- Examples: https://python.useinstructor.com/examples/
- Exa SDK cheat sheet (supplemental): https://docs.exa.ai/sdks/cheat-sheet
- Local ground truth: docs/developers/exa_py_api_reference.md, src/exa_direct/client.py, src/exa_direct/cli.py
