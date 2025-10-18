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

Poll (presets: fast=10s, balanced=30s, pro=40s):

```bash
exa research poll --id <researchId> --preset balanced
```

Stream (JSON-lines):

```bash
exa research stream --id <researchId> | jq .
```

### Context (Exa Code)

```bash
exa context query --query "pandas groupby examples" --tokensNum dynamic
```

#### Documentation (Exa Code)

- **Context (Exa Code):** <https://docs.exa.ai/reference/context>

### Examples

- See `examples/` for runnable scripts:
  - [`examples/search_examples.sh`](../../examples/search_examples.sh): search filters and inline contents
  - [`examples/contents_examples.sh`](../../examples/contents_examples.sh): contents options (text/highlights/summary/metadata)
  - [`examples/find_similar_examples.sh`](../../examples/find_similar_examples.sh): filters plus inline contents
  - [`examples/answer_examples.sh`](../../examples/answer_examples.sh): structured and streaming answers (JSON-lines)
  - [`examples/research_examples.sh`](../../examples/research_examples.sh): start/poll/stream/get/list flows
  - [`examples/context_example.sh`](../../examples/context_example.sh): Exa Code context queries
  - [`examples/stream_consumer.sh`](../../examples/stream_consumer.sh): pretty-prints JSON-lines
  - [`examples/agents_python.py`](../../examples/agents_python.py): Python agent helpers
  - [`examples/pipeline_search_contents_answer.py`](../../examples/pipeline_search_contents_answer.py):
    Search → Contents → Answer pipeline
  - [`examples/research_stream_json.py`](../../examples/research_stream_json.py): Research streaming (JSON-lines)
  - [`examples/context_rag_snippet.py`](../../examples/context_rag_snippet.py): Context for RAG prompts
  - [`examples/research_instructions.md`](../../examples/research_instructions.md): Research instructions template
  - [`examples/research_schema.json`](../../examples/research_schema.json): Research schema template

### Exa API Documentation

- **Search:** <https://docs.exa.ai/reference/search>
- **Contents:** <https://docs.exa.ai/reference/get-contents>
- **Find Similar:** <https://docs.exa.ai/reference/find-similar-links>
- **Answer:** <https://docs.exa.ai/reference/answer>
- **Research:**
  - **Create:** <https://docs.exa.ai/reference/research/create-a-task>
  - **Get/Stream:** <https://docs.exa.ai/reference/research/get-a-task>
  - **List:** <https://docs.exa.ai/reference/research/list-tasks>
- **Context (Exa Code):** <https://docs.exa.ai/reference/context>
- **Livecrawling Contents:** <https://docs.exa.ai/reference/livecrawling-contents>

#### Exa Research

##### Documentation (Exa Research)

- **Create:** <https://docs.exa.ai/reference/research/create-a-task>
- **Get/Stream:** <https://docs.exa.ai/reference/research/get-a-task>
- **List:** <https://docs.exa.ai/reference/research/list-tasks>
