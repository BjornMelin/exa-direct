# Logging

This project uses `structlog` to emit structured JSON by default and human-oriented console output when requested.
The configuration lives in `src/exa_direct/structured_logging.py` and is applied once at CLI startup before argument
parsing begins.

## Configuration Pipeline

`structured_logging.configure()` builds a processor chain shared by every command:

1. `structlog.contextvars.merge_contextvars` injects request, workflow, or agent identifiers bound in the current context.
2. `structlog.processors.TimeStamper(fmt="iso")` records the event timestamp.
3. `structlog.stdlib.add_log_level` and `add_logger_name` annotate severity and logger origin.
4. `structlog.processors.StackInfoRenderer()` and `format_exc_info` attach diagnostic data when `exc_info=True`.
5. A renderer selected by `EXA_DIRECT_LOG_FORMAT`:
   - `json` (default): `structlog.processors.JSONRenderer()` for machine ingestion.
   - `console`: `structlog.dev.ConsoleRenderer()` for local debugging.

The logger factory is `structlog.stdlib.LoggerFactory()`, so libraries that still use the logging
module continue to work without changes.

## Context Management

Use `structured_logging.bind()` to attach identifiers for the duration of a workflow run. The helper:

- Binds non-`None` key/value pairs via `structlog.contextvars.bind_contextvars`.
- Returns a context manager that unbinds the same keys on exit.

Workflow execution binds a generated `workflow_id`, so every `workflow.start` / `workflow.succeeded` pair
shares the same identifier.

## Emitted Events

Every workflow emits lifecycle events:

- `workflow.start`: validated inputs with `None` values removed (redacted by default).
- `workflow.plan`: ordered plan steps when a planner is present.
- `workflow.step`: emitted by `WorkflowContext.log_step()` to mark step progress (`status="start"|"success"|...`).
- `workflow.retry`: emitted by `WorkflowContext.log_retry()` when runners retry operations.
- `workflow.succeeded`: serialized outputs (`model_dump(exclude_none=True)`), also redacted by default.

Additional logging inside workflows should reuse `WorkflowContext.log_step()` / `log_retry()` or
`structured_logging.get_logger()` to preserve bound context.

## Environment Controls

| Variable | Purpose | Default |
| --- | --- | --- |
| `EXA_DIRECT_LOG_FORMAT` | `json` or `console`; any other value falls back to `json`. | `json` |
| `EXA_DIRECT_LOG_REDACT` | `1` (default) redacts sensitive keys / long strings; set to `0`, `false`, or `no` to log payloads verbatim. | `1` |

No other flags change logging behaviour. To adjust processors or renderers,
modify `structured_logging._shared_processors()` and rerun quality gates.
