# Troubleshooting

## Common Issues

### 401/403 Unauthorized

- Symptom: HTTP 401/403 from Exa endpoints.
- Fix: Ensure `EXA_API_KEY` is exported, present in a local `.env`, or pass
  `--api-key` on the command line. Optional helpers (`OPENAI_API_KEY`,
  `EXA_DIRECT_ENABLE_OPENAI`) follow the same environment/.env patterns.
- Check: `echo $EXA_API_KEY` should print a non-empty value.

### Empty or slow responses

- Use `--type fast` for latency-sensitive searches (see <https://docs.exa.ai/reference/how-exa-search-works>).
- Avoid `--text`/`--highlights` unless necessary (they increase payload size).
- Prefer `--livecrawl preferred` to balance freshness and reliability (<https://docs.exa.ai/reference/livecrawling-contents>).

### Context HTTP/2 negotiation failures

- Symptom: Errors such as `RemoteProtocolError: HTTP/2 negotiation failed`.
- Fix: The CLI automatically retries and downgrades to HTTP/1.1. Ensure you are
  running the latest version; no manual flag changes are required unless a proxy
  blocks HTTP/1.1 entirely.
- Optional: Install `httpx[http2]` to regain HTTP/2 if it was removed; the CLI
  will resume using it when negotiations succeed.

### Research stream shows no events

- Verify the `researchId` from `research start`.
- Try polling (`exa research poll --id <id>`) if the environment blocks streaming.
- Confirm connectivity and that the task is still running.

### JSON parsing errors

- If you use `@file` for `--instructions` or `--schema`, ensure the file exists and is valid UTF-8.
- For `--schema`, the file must be valid JSON and follow JSON Schema draft-07.

### Large outputs

- Use `--save out.json` to write results to disk and pipe `--pretty` for readability.

## Diagnostic Tips

- Add `--pretty` to inspect payload structure.
- Use `jq` to filter (`... | jq '.results[0]'`).
- For streaming, pipe to file: `exa research stream --id <id> > stream.log`.

## References

- Exa API overview: <https://exa.ai/blog/exa-api-2-0>
- Search: <https://docs.exa.ai/reference/search>
- Contents: <https://docs.exa.ai/reference/get-contents>
- Find Similar: <https://docs.exa.ai/reference/find-similar-links>
- Answer: <https://docs.exa.ai/reference/answer>
- Research (Create/Get/List):
  - <https://docs.exa.ai/reference/research/create-a-task>
  - <https://docs.exa.ai/reference/research/get-a-task>
  - <https://docs.exa.ai/reference/research/list-tasks>
- Context (Exa Code): <https://docs.exa.ai/reference/context>
