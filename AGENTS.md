# AGENTS.md – exa-direct CLI Agent Guide

## Purpose

- This file equips an AI coding agent to use the exa-direct CLI autonomously and correctly,
  with clear triggers, parameter choices, and examples.
  Treat this as your operating manual when assisting users in new sessions with no prior context.

## Environment Assumptions

- Project path: /home/bjorn/repos/exa-direct
- Runtime: Python 3.10+
- CLI entry: `exa`
- Required env var: `EXA_API_KEY` (present) – if missing, ask once for a key or a temporary override via `--api-key`.
- Output format: JSON to stdout by default; `--pretty` prints indented JSON; `--save path.json` writes to file.

## Autonomy Rules (When to Run Which Command)

- Search (fast/auto/neural/keyword)
  - Trigger: User needs relevant links/sources or to discover material on a topic.
  - Choose `--type fast` when latency matters (interactive workflows); `auto` for balanced general queries;
    `neural` for semantic intent; `keyword` for exact literal matching (e.g., legal entity names).
  - Add `--text` only when the downstream step requires page text. Avoid text for large batches unless necessary.
  - Use domain filters when the user mentions specific sources; date bounds when recency matters.
  - Then, if the user wants detail extraction, follow with Contents.
- Contents (with livecrawling)
  - Trigger: We already have URL(s) and need page text/highlights.
  - Use `--livecrawl preferred` for recency-sensitive topics with fallback; `always` only for strictly live data;
    `fallback` for speed bias; `never` for historical/static content.
  - Add `--text` when the next step consumes full text; `--highlights` when highlights suffice.
- Find Similar
  - Trigger: Pivot to related pages starting from a known URL (e.g., “find more like this paper/post”).
- Answer vs Research
  - Use `answer` for simple, single-shot Q&A with citations.
  - Use `research` when: multi-step investigation, structured output (JSON Schema), or a synthesized report.
- Research (create/get/list/poll/stream)
  - Trigger: Complex tasks (e.g., “Compare XYZ, return a table”; “Provide a sourced, structured report”).
  - Model selection: `exa-research-fast` (quick iteration), `exa-research` (balanced), `exa-research-pro` (thorough reasoning).
  - Poll presets: fast=10s, exa-research=30s, pro=40s. Override `--interval` if the user asks for different cadence.
  - Stream SSE: Use when the user wants progress and partials; prints only event-stream lines to stdout (no trailing JSON).
- Context (Exa Code)
  - Trigger: User needs code examples, setup snippets, library usage, or token-efficient coding context.
  - `--tokensNum dynamic` by default. Increase (e.g., 5000–10000) if the agent needs broader context blocks.

## Command Cheatsheet (copy/paste)

- Search (Fast):
  - `exa search --query "<text>" --type fast --pretty`
  - Optional filters: `--include-text word1 word2` (must-appear terms), `--exclude-text word3`.
- Search (Auto + domain include/exclude + dates):
  - `exa search --query "<text>" --type auto --include-domains a.com b.com --exclude-domains x.com \
    --start-published-date 2025-01-01 --end-published-date 2025-12-31 --pretty`
- Contents (livecrawling preferred):
  - `exa contents https://example.com https://another.example --text --livecrawl preferred --pretty`
- Find Similar:
  - `exa find-similar --url https://arxiv.org/abs/2307.06435 --num-results 5 --exclude-source-domain --pretty`
- Answer:
  - `exa answer --query "What changed in Exa 2.0?" --pretty`
- Research (Create with schema + fast):
  - `exa research start --instructions @examples/research_instructions.md --schema @examples/research_schema.json --model exa-research-fast --pretty`
- Research (Get/Events):
  - `exa research get --id <researchId> --events --pretty`
- Research (Poll with preset):
  - `exa research poll --id <researchId> --model exa-research --timeout 900 --pretty`
- Research (Stream SSE):
  - `exa research stream --id <researchId>`
- Research (List):
  - `exa research list --limit 10 --pretty`
- Context (Exa Code):
  - `exa context query --query "pandas groupby examples" --tokensNum dynamic --pretty`

## Advanced Tips (from Deep Research, 2025-10-16)

- Search types and expected behavior:
  - Auto: balanced; good default for varied queries.
  - Fast: latency-optimized (<~400 ms p50 end-to-end in typical cases); use for interactive flows.
  - Neural: semantic exploration; higher recall for concept-heavy queries.
  - Keyword: literal matching; use for exact phrases/jargon.
- Contents retrieval modes:
  - `--text` returns full page text (larger payloads, more cost/latency).
  - `--highlights` extracts short snippets for quick triage.
  - Prefer highlights when skimming; use text when downstream LLM needs full content.
- Livecrawling choices:
  - `preferred` (recommended default): try live, fallback to cache.
  - `always`: only when strict freshness required; expect occasional failures/timeouts.
  - `fallback`/`never`: speed/cost bias or historical snapshots.
  - For responsiveness, keep `livecrawlTimeout` low (e.g., ~1000 ms) when hitting many URLs (via cURL helpers).
- Answer vs Research:
  - Answer: synchronous Q&A with citations; fastest path but unstructured.
  - Research: asynchronous, supports structured outputs (JSON Schema), polling or SSE streaming.
  - Schema guidance: ≤10 top-level fields, shallow nesting (≤2), add `description` per field; split oversized tasks.
- Research operations:
  - Model pick: `exa-research-fast` (<~30 s light tasks), `exa-research` (1–2 min balanced),
    `exa-research-pro` (>2 min deep analysis).
  - Polling: CLI presets map to model (fast=10s, default=30s, pro=40s).
    Use `--interval 3` if you require tighter polling; prefer `stream` for real-time.
  - SSE stream prints only event lines; do not expect trailing JSON.
- Context (Exa Code):
  - Use `--tokensNum dynamic` by default; raise (e.g., 2048, 5000+) when more context helps.
- Common pitfalls and mitigations:
  - Missing `EXA_API_KEY` → set env or pass `--api-key` once.
  - Large payloads → prefer `--highlights`, batch fewer URLs, or disable livecrawl.
  - Ambiguous instructions → refine prompts, include schemas/examples.
  - High polling overhead → switch to `research stream` or widen `--interval`.

## Heuristics & Parameter Recipes

- Choosing search type:
  - fast: use for conversational/interactive runs and when doing many searches (agents, iterative queries).
  - auto: default when unsure; balanced recall/precision.
  - neural: deep semantic intent matching; good for concept-heavy queries.
  - keyword: exact matching (proper nouns, quoted terms, identifiers).
- When to include text/highlights:
  - Use `--text` if your next step (answering/summarizing/LLM) needs the full content.
  - Use `--highlights` for quick skim tasks or when building a shortlist.
- Livecrawling:
  - `preferred`: production-safe freshness; falls back to cache.
  - `always`: only when you require current content and can accept failures on crawl issues.
  - `fallback`: use cache unless missing (speed bias).
  - `never`: historical snapshots or static docs.
- Research model pick:
  - fast: <~1 min typical; sketch or small schema.
  - exa-research: balanced (1–2 min typical); default for general reports.
  - pro: deeper, longer runs (>2 min typical); complex schemas.
- Research schema tips:
  - Keep root fields ≤ 8; shallow nesting (≤ 5 levels).
  - Prefer enums/typed fields for precision.
  - Split large outputs into multiple tasks rather than one giant schema.

## When to Ask Clarifying Questions (blocking only)

- Missing query text or contradictory constraints (e.g., user wants “all data” but insists on `--type keyword` only).
- Research without clear instructions or schema when structured output is explicitly requested.
- Context query missing the language/framework focus (ask 1 question to narrow target).

## Error/Edge Handling (agent actions)

- 401/403: ask for `EXA_API_KEY` or use `--api-key` one-time override.
- Large outputs: add `--save out.json` and tell the user where it was written.
- SSE in restricted environments: switch to `research poll`.

## Decision Matrix (quick reference)

- Search type: fast (latency) > auto (balanced) > neural (semantic) > keyword (exact).
- Answer vs Research: simple Q&A → Answer; multi-step/structured → Research.
- Livecrawling: preferred for freshness; always for strict real-time; fallback/never for speed or static data.

## Autonomous Triggers (examples)

- "Find recent posts about `<topic>` and summarize" →
  run `search --type fast --text` then pipe to `answer` or `research` (if structure requested).
- "Give me 5 similar sources to this" → `find-similar --url "<link>"` with `--num-results`.
- “Create a table comparing X/Y/Z with fields …” → `research start` with `@schema.json`; then `poll` or `stream`.
- "I need code examples for `<library>` `<topic>`" → `context query --tokensNum dynamic`.

## Agent Routing (Copy/Paste)

Use this snippet in your own AGENTS.md to enable GPT‑5‑Codex/GPT‑5 agents to call the Exa CLI deterministically.

- Tool: `exa` (CLI)
- Env: requires `EXA_API_KEY`; or pass `--api-key` per call.
- Output: JSON to stdout; add `--pretty` and/or `--save path.json`.

### When to call

- Find sources/links → `exa search --query "…" [--type fast|auto] [filters]`
- Fetch contents/highlights → `exa contents <urls…> [--text] [--highlights] [--livecrawl preferred]`
- Find similar → `exa find-similar --url <url> [--exclude-source-domain]`
- Answer with citations → `exa answer --query "…" [--include-text]`
- Long-form research (schema recommended):
  - Create → `exa research start --instructions "…" [--model exa-research|exa-research-pro] [--schema @schema.json] [--infer-schema]`
  - Get → `exa research get --id <id> [--events]`
  - List → `exa research list [--limit N] [--cursor CUR]`
  - Poll → `exa research poll --id <id> [--model exa-research[-fast|-pro]] [--interval SECS] [--timeout 900]`
  - Stream → `exa research stream --id <id> [--json-events]`
- Code context → `exa context query --query "…" --tokensNum dynamic`

### Defaults

- Models: `exa-research-fast` (fast), `exa-research` (balanced), `exa-research-pro` (thorough).
- Prefer schema-driven outputs (≤8 top-level fields, shallow nesting, add descriptions).
- Livecrawling: use `preferred` for freshness; `always` only when strictly required.

### Safety & limits

- Back off on 429/5xx; use `--type fast` for interactive loops.
- Always capture stdout JSON; use `--save` to persist.

## References (read when needed)

- API overview: https://exa.ai/blog/exa-api-2-0
- Search: https://docs.exa.ai/reference/search
- Contents: https://docs.exa.ai/reference/get-contents
- Find Similar: https://docs.exa.ai/reference/find-similar-links
- Answer: https://docs.exa.ai/reference/answer
- Research (create/get/list): https://docs.exa.ai/reference/research/create-a-task, https://docs.exa.ai/reference/research/get-a-task, https://docs.exa.ai/reference/research/list-tasks
- Context (Exa Code): https://docs.exa.ai/reference/context
- Livecrawling: https://docs.exa.ai/reference/livecrawling-contents
