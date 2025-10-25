# ADR-0017: Agent Output Contract (NDJSON + Final JSON)

Date: 2025-10-19
Status: Accepted (contract-only; used by agent-ready seam and any pilot).

## Decision

- Streaming: adopt OpenAI Responses API event stream verbatim as `application/x-ndjson`. Each line is a JSON
  object with an `event`/`type` and associated payload (e.g., `response.output_text.delta`,
  `response.function_call_arguments.delta`, `response.completed`, `error`).
- Final object: enforce `json_schema` strict final JSON (no additionalProperties; all required present). The final
  event payload must include the fully assembled object; CLI will emit the final object as the last non-event line
  when `--no-stream` is used or as a `final` event when streaming.

## Example (abbreviated)

NDJSON stream (lines):

```
{"type":"response.created","response_id":"resp_..."}
{"type":"response.function_call_arguments.delta","tool_call_id":"tool_1","delta":"{\"query\":\"rust async cancellation\""}
{"type":"response.function_call_arguments.delta","tool_call_id":"tool_1","delta":"}"}
{"type":"response.function_call_arguments.done","tool_call_id":"tool_1"}
{"type":"response.output_text.delta","delta":"Top findings: ..."}
{"type":"response.completed"}
{"type":"final","content":{"summary":"...","sources":["https://...","https://..."]}}
```

Schema (excerpt):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["summary", "sources"],
  "properties": {
    "summary": {"type": "string", "minLength": 1},
    "sources": {"type": "array", "items": {"type": "string", "format": "uri"}}
  }
}
```

## Error Handling

- Any stream `error` event must be forwarded as-is and cause non-zero exit unless `--ignore-errors` is set.
- Timeouts mapped to a dedicated exit code; partial streams retained in logs for diagnostics.

## Rationale

- Zero bespoke protocol work; maximum leverage of upstream event taxonomy.
- Determinism: strict final JSON enables reliable CLI-to-automation handoffs and tests.

## References

- OpenAI Responses streaming/events: https://platform.openai.com/docs/guides/function-calling
- Exa SDK streaming examples: https://docs.exa.ai/sdks/cheat-sheet
