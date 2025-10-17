# Commands & Examples

## Common Flags

- `--api-key`: Override `EXA_API_KEY`.
- `--pretty`: Indented JSON output.
- `--save <file>`: Save JSON to a file.

## Search

```bash
exa search --query "2025 LLM agent benchmarks" --type fast --text --pretty
```

Options:

- `--type`: `auto|neural|keyword|fast` (see <https://docs.exa.ai/reference/how-exa-search-works>)
- Include/exclude domains; date bounds; include/exclude text terms.
Docs: <https://docs.exa.ai/reference/search>

## Contents

```bash
exa contents https://example.com --text --livecrawl preferred
```

Options:

- `--text`, `--highlights`
- `--livecrawl`: `always|preferred|fallback|never` (<https://docs.exa.ai/reference/livecrawling-contents>)
Docs: <https://docs.exa.ai/reference/get-contents>

## Find Similar

```bash
exa find-similar --url https://arxiv.org/abs/2307.06435 --num-results 5
```

Docs: <https://docs.exa.ai/reference/find-similar-links>

## Answer

```bash
exa answer --query "What changed in Exa 2.0?" --pretty
```

Docs: <https://docs.exa.ai/reference/answer>

## Research

Create:

```bash
exa research start --instructions @examples/research_instructions.md \
  --schema @examples/research_schema.json --model exa-research-fast
```

Get:

```bash
exa research get --id <researchId> [--events]
```

List:

```bash
exa research list --limit 10
```

Poll (presets: fast=10, exa-research=30, pro=40 seconds):

```bash
exa research poll --id <researchId> --model exa-research
```

Stream (JSON-lines):

```bash
exa research stream --id <researchId> | jq .

### Examples

- See `examples/search_examples.sh`, `examples/contents_examples.sh`, `examples/find_similar_examples.sh`, `examples/answer_examples.sh`, `examples/research_examples.sh`, and `examples/context_example.sh`.
```

Docs:

- Create: <https://docs.exa.ai/reference/research/create-a-task>
- Get/Stream: <https://docs.exa.ai/reference/research/get-a-task>
- List: <https://docs.exa.ai/reference/research/list-tasks>

## Context (Exa Code)

```bash
exa context query --query "pandas groupby examples" --tokensNum dynamic
```

Docs: <https://docs.exa.ai/reference/context>
