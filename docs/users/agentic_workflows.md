# Agentic Workflows

`exa-direct` ships an optional integration with the OpenAI Agents SDK that can
coordinate all built-in workflows (search, contents, find-similar, answer,
research, context) via a coordinator agent and one specialist per workflow.

Enable it by installing `openai-agents` and setting the toggle:

```
export EXA_DIRECT_ENABLE_OPENAI=1
export OPENAI_API_KEY=sk-...
```

## Quickstart: CLI

Run a coordinator over a prompt. The coordinator will decide which specialist(s)
to call and in what order.

```
exa agents run --input "Find recent RAG benchmarks and summarize" --pretty
```

Optional model/session overrides:

```
exa agents run --input "Competitive landscape for vector DBs" \
  --model gpt-5-mini --specialist-model gpt-5-low \
  --session-id team-thread-1 --session-backend sqlite --session-db /tmp/exa_agents.db
```

## Python API

```python
from exa_direct.integrations import agents
from exa_direct.integrations.agents import CoordinatorSettings, WorkflowAgentContext

settings = CoordinatorSettings(model="gpt-5-mini", specialist_model="gpt-5-low", max_turns=8)
context = WorkflowAgentContext(conversation_id="demo")
result = await agents.run_coordinator(
    "Draft a plan for a content audit of our docs",
    settings=settings,
    context=context,
    session_id="demo",
    session_backend="sqlite",
    session_db_path=":memory:",
)
print(getattr(result, "final_output", None))
```

## Example Prompts by Tooling Path

- Search + Contents (fresh sources and triage → fetch text if needed)
  - "Find the latest official docs for Next.js Partial Prerendering and extract the step-by-step setup."
  - "Collect 5 credible sources about vector DB HNSW tradeoffs;
    fetch highlights, then pull full text for any source with benchmarks"

- Answer (quick factual Q&A with citations)
  - "What’s the capital of Japan? Provide two citations."
  - "Summarize the key differences between BM25 and dense retrieval in 4 bullets with sources."

- Research (multi-source synthesis or structured output)
  - "Create a table comparing RAG evaluation frameworks (Ragas, G-Eval, DeepEval)
    with columns: metrics, dataset support, licensing, links."
  - "Survey 2024–2025 LLM routing techniques and produce a numbered list of approaches with tradeoffs and references."

- Find Similar (neighbor discovery)
  - "Given https://arxiv.org/abs/2307.06435 find similar papers;
    prefer survey articles and fetch highlights."

- Code Context (exa-code)
  - "Django async views examples and caveats for database access; include links."

### Chaining Tips

- For triage: start with `exa_search` (or `search_cli`) with highlights;
  then call `exa_contents` with selected URLs to fetch text or summaries.
- For synthesis: after gathering sources, use `answer_cli` for short summaries,
  or `research_run` for tables and multi-source aggregation.
- For neighbor exploration: call `exa_find_similar` on a strong seed URL;
  if results look promising, follow up with `exa_contents`.
- Validation loop: if uncertain or missing details, refine queries (date filters,
  domain filters), call tools again, and cross-verify from multiple sources.

## Environment Variables

- `EXA_DIRECT_ENABLE_OPENAI`: `1` to enable Agents integration.
- `EXA_DIRECT_AGENTS_MODEL`: default coordinator model (fallback chain applies).
- `EXA_DIRECT_AGENTS_COORDINATOR_MODEL`: coordinator model override.
- `EXA_DIRECT_AGENTS_SPECIALIST_MODEL`: specialist model; defaults to coordinator.
- `EXA_DIRECT_AGENTS_SESSION_BACKEND`:
  - `none`: no session backend
  - `sqlite`: SQLite session backend
  - `advanced_sqlite`: Advanced SQLite session backend
  - default: `sqlite` when a session id is present, else `none`
- `EXA_DIRECT_AGENTS_SESSION_DB`: `:memory:` or path to a SQLite DB file.
- `EXA_DIRECT_AGENTS_SESSION_ID`: implicit session id when not passed explicitly.

## Notes

- Tools are generated from workflow schemas and run via the coordinator. Strict
  JSON schema is disabled for function tools to support kwargs-style inputs.
- Sessions (SQLite/AdvancedSQLite) are optional and created only when a session id
  is provided or configured via env. See the OpenAI Agents SDK docs for details.
