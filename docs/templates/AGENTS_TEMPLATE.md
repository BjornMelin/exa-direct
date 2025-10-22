# AGENTS.md – exa-direct CLI Agent Instructions

## Invocation Rules

- Prefer the CLI (`exa ...`) for discrete operations (search, contents, find-similar, answer, research, context, workflow).
- Prefer the `workflow` commands when a higher-level, typed flow exists or when tool schemas are needed.
- Use streaming modes only when the consumer can parse chunked output (see Streaming).
- Always print raw JSON to stdout; use `--pretty` only for human-facing logs.

## Global Flags (apply to every command)

- `--pretty`: human-readable JSON output (avoid for machine parsing).
- `--save <path>`: also write JSON to a file (stdout still prints JSON).

## Commands (capsule summaries)

### search

Find links, optionally with contents.

```bash
exa search --query "<text>" [--type auto|neural|keyword|fast|hybrid|deep]
           [--num-results N]
           [--include-domains d1 d2 ...] [--exclude-domains d1 d2 ...]
           [--start-published-date YYYY-MM-DD] [--end-published-date YYYY-MM-DD]
           [--start-crawl-date YYYY-MM-DD]    [--end-crawl-date YYYY-MM-DD]
           [--include-text w1 w2 ...] [--exclude-text w1 w2 ...]
           [--use-autoprompt] [--category <name>] [--user-location CC]
           [--moderation]
           # contents toggles (see Contents Options) trigger search_and_contents
           [--text] [--text-max-characters N] [--text-include-html-tags]
           [--highlights] [--highlights-num-sentences N]
           [--highlights-per-url N] [--highlights-query Q]
           [--summary-query Q] [--summary-schema @file.json]
           [--metadata | --metadata-json @file.json]
           [--subpages N] [--subpage-target URL[,URL...]]
           [--extras-links N] [--extras-image-links N]
           [--context] [--context-max-characters N]
           [--livecrawl always|preferred|fallback|never|auto]
           [--livecrawl-timeout ms]
           [--filter-empty-results] [--contents-flags f1 f2 ...]
```

### contents

Fetch page contents for one or more URLs.

```bash
exa contents <url1> [<url2> ...]  # supports the same Contents Options set
```

### find-similar

Find similar pages for a URL (optionally fetch contents for results).

```bash
exa find-similar --url <source>
                  [--num-results N] [--exclude-source-domain]
                  [--include-domains ...] [--exclude-domains ...]
                  [--include-text ...] [--exclude-text ...]
                  [--start-published-date ...] [--end-published-date ...]
                  [--start-crawl-date ...]     [--end-crawl-date ...]
                  [--category <name>]
                  # contents toggles (see Contents Options)
                  [... contents flags ...]
```

### answer

Get a synthesized answer with citations; supports text streaming and JSON-lines.

```bash
exa answer --query "<question>" [--include-text]
           [--stream] [--json-lines]
           [--model exa|exa-pro]
           [--system-prompt "<system>"]
           [--output-schema @file.json]
           [--user-location CC]
```

### research

Long-running research tasks with polling/streaming.

```bash
exa research start --instructions "text or @file.md" [--model exa-research-fast|exa-research|exa-research-pro] [--schema @file.json]
exa research get   --id <researchId> [--events]
exa research list  [--limit N] [--cursor CUR]
exa research poll  --id <researchId> [--preset fast|balanced|pro]  # preset is UX-only
exa research stream --id <researchId>  # emits JSON-lines
```

### context (Exa Code)

Lightweight examples/code context API.

```bash
exa context query --query "<text>" [--tokensNum dynamic|<int>]
```

### workflow

Introspect and run typed workflows exposed by the app.

```bash
exa workflow list [--format json|table]
exa workflow describe <name> [--schema]
exa workflow run <name> [--plan|--dry-run]
                     [--param KEY=VALUE ...]
                     [--input @file.json | '{"k":"v"}']
```

## Contents Options (shared flags)

- Text: `--text` | `--text-max-characters N` | `--text-include-html-tags`
- Highlights: `--highlights` | `--highlights-num-sentences N` | `--highlights-per-url N` | `--highlights-query Q`
- Summary: `--summary-query Q` | `--summary-schema @file.json`
- Metadata: `--metadata` | `--metadata-json @file.json`
- Subpages: `--subpages N` | `--subpage-target URL[,URL...]`
- Extras: `--extras-links N` | `--extras-image-links N`
- Context: `--context` | `--context-max-characters N`
- Livecrawl: `--livecrawl always|preferred|fallback|never|auto` | `--livecrawl-timeout ms`
- Filters/Flags: `--filter-empty-results` | `--contents-flags f1 f2 ...`

## When to Use Workflows vs Direct Commands

- Use `workflow run` when: you need stable JSON Schemas, multi-step orchestration, or to expose tools to agent frameworks that consume function/tool schemas.
- Use direct commands (`search`, `contents`, `answer`, `research`, `context`) for single-step tasks or ad‑hoc shell flows.

## Streaming

- `exa answer --stream` prints plain text chunks; add `--json-lines` for structured events (`{"event":"chunk","data":"..."}` and final `{"event":"done"}`).
- `exa research stream` always prints JSON-lines; parse one object per line.

## Parsing & Persistence

- Default output is a single JSON object to stdout. Agents should capture stdout and parse as JSON.
- With `--save <path>`, a copy is written to disk in addition to stdout.

## Error Handling

- Non-zero exit code indicates failure. The CLI emits a short error message to stderr.
- Validation errors from workflows return Pydantic-formatted messages; fix argument names or payload schemas.

## Guidelines

- Discover available tools and their schemas with `workflow list` and `workflow describe <name> --schema`.
- Prefer `workflow run` with `--param KEY=VALUE` and/or `--input @file.json` for typed, deterministic execution.
- Use `--pretty` only for human inspection; omit for programmatic parsing.
- For tasks that must complete before proceeding, prefer single-object results (e.g., `research poll`) over streaming.
- When streaming (`answer --stream --json-lines`, `research stream`), consume one JSON object per line and aggregate until a terminal status.
- Treat CLI calls as idempotent where possible; capture JSON from stdout and avoid parsing prettified output.

## Minimal Examples

```bash
# Quick search with inline contents
exa search --query "2025 LLM agent benchmarks" --type fast --text --num-results 5

# Fetch highlights and a summary for specific URLs
exa contents https://example.com https://another.example \
  --highlights --highlights-num-sentences 3 \
  --summary-query "Key takeaways"

# Answer with streaming JSON-lines
exa answer --query "Summarize latest RAG evals" --include-text --stream --json-lines

# Start + poll a research task
exa research start --instructions @docs/prompts/rag_eval.md --model exa-research \
  --schema @docs/schemas/rag_eval.json
exa research poll --id <researchId>

# List and run a workflow
exa workflow list
exa workflow run search_cli --param query="best RAG papers 2025" --plan
```

---

## Agent Safety Defaults

- Never pass secrets on command line unless required; use environment variables.
- Keep `--pretty` off for machine parsing to reduce token usage and ambiguity.
- Use `--plan` to preview workflow actions before running destructive steps.
