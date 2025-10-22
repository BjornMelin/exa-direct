# Workflow Engine Guide

The workflow registry in `exa-direct` collects every reusable automation path.
It powers the CLI (`exa workflow ...`), OpenAI Responses function tools, and the
Agents SDK integration. All workflows share the same typed input/output models
and exported JSON Schemas under [`docs/schemas/`](../schemas/).

## Built-in Workflows

| Name | Purpose | Input Schema | Output Schema |
| --- | --- | --- | --- |
| `search_cli` | Single-step search command | [search_cli_input.json](../schemas/search_cli_input.json) | [search_cli_output.json](../schemas/search_cli_output.json) |
| `contents_cli` | Fetch contents for URLs | [contents_cli_input.json](../schemas/contents_cli_input.json) | [contents_cli_output.json](../schemas/contents_cli_output.json) |
| `find_similar_cli` | Similarity + optional contents | [find_similar_cli_input.json](../schemas/find_similar_cli_input.json) | [find_similar_cli_output.json](../schemas/find_similar_cli_output.json) |
| `answer_cli` | Answer generation | [answer_cli_input.json](../schemas/answer_cli_input.json) | [answer_cli_output.json](../schemas/answer_cli_output.json) |
| `search_collect` | Search with optional inline contents | [search_collect_input.json](../schemas/search_collect_input.json) | [search_collect_output.json](../schemas/search_collect_output.json) |
| `research_run` | Submit/poll an Exa research task | [research_run_input.json](../schemas/research_run_input.json) | [research_run_output.json](../schemas/research_run_output.json) |
| `context_build` | Query the code context endpoint | [context_build_input.json](../schemas/context_build_input.json) | [context_build_output.json](../schemas/context_build_output.json) |

## CLI Usage

The CLI exposes the registry through the `workflow` command group:

```bash
# List registered workflows
exa workflow list

# Inspect a workflow, including schemas and plan steps
exa workflow describe search_collect --schema

# Execute a workflow using inline parameters
exa workflow run search_collect \
  --param query="hybrid search vector databases" \
  --param fetch_contents=true

# Execute with JSON payloads (supports @file syntax)
exa workflow run research_run --input @examples/research_payload.json

# Preview the plan without running
exa workflow run search_collect --plan
```

Each CLI execution logs structured lifecycle events (`workflow.start`,
`workflow.plan`, `workflow.step`, `workflow.succeeded`) through `structlog`.
Set `EXA_DIRECT_LOG_FORMAT=console` for human-readable output or leave the
(default) JSON renderer for ingestion by log pipelines. To disable payload
redaction entirely, export `EXA_DIRECT_LOG_REDACT=0`.

## OpenAI Responses Function Tools

Every workflow can be exposed as a function tool when
`EXA_DIRECT_ENABLE_OPENAI=1` and valid `OPENAI_API_KEY` credentials are
available. Example:

```python
from openai import OpenAI
from exa_direct.integrations.responses import workflow_function_tool

client = OpenAI()
tool = workflow_function_tool("search_collect")

response = client.responses.create(
    model="gpt-4.1",
    input="Find recent retrieval-augmented search articles",
    tools=[{"type": "function", **tool.__dict__}],
)
```

The handler executes the workflow via the shared registry and redacts
sensitive fields before logging.

## Agents SDK Integration

`exa_direct.integrations.agents.workflow_tool()` wraps workflows for the
OpenAI Agents SDK. The helper returns a ready-to-register tool, handling API
key resolution and connection lifecycle. Enable the integration by setting
`EXA_DIRECT_ENABLE_OPENAI=1` and installing `openai-agents`.

Future work will add coordinator/specialist agent patterns, but the current
wrapper already ensures each workflow is callable through the Agents SDK’s
standard tool interface.

## Adding New Workflows

1. Create Pydantic input/output models in `workflows/builtins.py` (or a new
   module).
2. Implement the runner using `WorkflowContext.log_step()` to log progress.
3. Register a `WorkflowDefinition` with a concise summary and optional planner.
4. Export schemas by running `uv run python scripts/export_workflow_schemas.py`.
5. Update CLI/tests/docs as needed.

This workflow engine keeps orchestration DRY and makes every capability
available to the CLI, Codex, Responses, and Agents surfaces uniformly.
