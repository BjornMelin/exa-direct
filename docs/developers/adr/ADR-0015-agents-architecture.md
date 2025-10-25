# ADR-0015: Agent Architecture in exa-direct

Date: 2025-10-19
Status: Rejected (below ≥9.0/10 threshold). Proceed with agent-ready seam + optional pilot.

## Context

We evaluated adding an Agent component (or multi-agent) to exa-direct v0.1.0. Non-negotiables: deterministic
JSON/NDJSON, typed streaming, SDK-first (exa_py + OpenAI Python).

## Decision

- Do NOT add a full Agent component to the CLI at this time.
- Implement a thin, library-agnostic “agent-ready” seam (internal interface + tool registry, strict schemas, NDJSON)
  without exposing new CLI commands.
- Revisit after a narrow, validated pilot demonstrates ROI with metrics and HIL gating.

## Rationale (Decision Framework)

- Initial hypothesis (minimal single-agent via OpenAI Responses API) scored 9.18/10.
- After consensus (multi-model), risks around maintenance/evaluation/uncertain ROI adjusted the score to 7.875/10 < 9.0 threshold.
- Determinism and ops burden make a general agent premature; a seam preserves adaptability without committing to a framework.

## Consequences

- No user-facing `agent` command now; no multi-agent orchestration in CLI.
- Add internal `AgentPort` and tool registry to keep future integration small and deletable.
- Optional pilot lives behind `--experimental` when/if a workflow is validated.

## Alternatives Considered

- OpenAI Agents SDK in-CLI: higher-level primitives but still requires NDJSON bridging and evaluation infra.
- LangGraph service now: powerful, but would add orchestration complexity and persistence early.
- CrewAI/LlamaIndex in-CLI: increased maintenance and less native streaming determinism.

## References

- OpenAI Responses API (function calling & streaming): https://platform.openai.com/docs/guides/function-calling
- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/workflows-agents
- Exa SDK cheat sheet: https://docs.exa.ai/sdks/cheat-sheet
