# ADR-0016: Agent Framework Selection (Deferred with Direction)

Date: 2025-10-19
Status: Deferred (no full adoption now). Direction recorded for future pilot and beyond.

## Context

We compared OpenAI Responses API (function tools), OpenAI Agents SDK, LangChain+LangGraph, CrewAI, and LlamaIndex
for integrating an Agent capability into exa-direct.

## Direction (if/when a pilot proceeds)

- Pilot framework: OpenAI Responses API with `json_schema` strict outputs and native NDJSON streaming. Minimal glue;
  maps cleanly to our CLI contracts.
- For larger/multi-agent orchestration later: prefer hosting a LangGraph-based service (outside CLI) if justified by
  validated workflows and metrics. Do not embed orchestration in the CLI.

## Rationale

- Responses API directly satisfies our determinism constraints and stream format; lowest maintenance for a single,
  tool-driven agent.
- Agents SDK provides higher-level features but still needs NDJSON event bridging and increases coupling.
- LangGraph/CrewAI/LlamaIndex increase complexity; streaming determinism requires additional adapters.

## Non-Goals (now)

- No multi-agent team orchestration in the CLI.
- No persistence, sessions, or checkpointers in CLI.

## Acceptance Criteria for Future Re-evaluation

- ≥2–3 repeatable, tool-heavy workflows with measured ROI (time saved, resolution rate).
- Evaluation harness in place (success metrics, fallback rate, cost/latency budgets).
- Safety/guardrails and human-in-the-loop policies defined for side-effecting tools.

## References

- Responses API structured outputs: https://cookbook.openai.com/examples/structured_outputs_multi_agent
- Agents SDK quickstart/streaming: https://openai.github.io/openai-agents-python/
- LangGraph: https://docs.langchain.com/oss/python/langgraph/workflows-agents
