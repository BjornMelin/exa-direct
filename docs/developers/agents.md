# Agents SDK Integration

The coordinator exposes every workflow as a typed tool for the OpenAI Agents SDK.
Enable it by installing `openai-agents`, setting `EXA_DIRECT_ENABLE_OPENAI=1`,
and configuring your OpenAI credentials.

```
export EXA_DIRECT_ENABLE_OPENAI=1
export OPENAI_API_KEY=sk-...
```

```python
from exa_direct.integrations import agents
from exa_direct.integrations.agents import (
    CoordinatorSettings,
    WorkflowAgentContext,
)

settings = CoordinatorSettings(model="gpt-4.1")
context = WorkflowAgentContext(conversation_id="demo")

coordinator, specialists = agents.build_coordinator(settings=settings)
print([spec.name for spec in specialists])
```

Use `agents.run_coordinator()` to orchestrate multi-step flows:

```python
import asyncio

async def demo():
    result = await agents.run_coordinator(
        "Find RAG benchmarks and summarise the latest ones",
        context=WorkflowAgentContext(conversation_id="demo"),
        settings=CoordinatorSettings(model="gpt-4.1-mini", max_turns=8),
    )
    print(getattr(result, "final_output", None))

asyncio.run(demo())
```

## Guardrails & Observability

* **Budget controls** – configure `step_budget`, `cost_budget_tokens`, and
  `max_steps`.
* **Structured logging** – lifecycle events emit `agents.coordinator.*` and
  `agents.specialist.*` logs with redacted payloads.
* **Tool contracts** – each workflow reuses its Pydantic schema for input and
  output validation. Invalid payloads raise errors instead of partial results.

## Testing

The coordinator and specialists are fully covered by unit tests. To skip the
Agents SDK tests, set `EXA_DIRECT_ENABLE_OPENAI=0` or uninstall
`openai-agents`.
