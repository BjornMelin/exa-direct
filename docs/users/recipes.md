# Recipes

Practical, copy‑paste workflows that combine multiple `exa` commands.

## Search → Contents (Highlights) → Answer

```bash
exa search --query "hybrid vector search" --type fast --pretty --save /tmp/search.json
URL1=$(jq -r '.results[0].url // .data[0].url' /tmp/search.json)
URL2=$(jq -r '.results[1].url // .data[1].url' /tmp/search.json)
exa contents "$URL1" "$URL2" --highlights --pretty --save /tmp/contents.json
exa answer --query "Summarize hybrid vector search" --pretty
```

See also: `examples/pipeline_search_contents_answer.py`.

## Research (Start → Stream JSON → Final)

```bash
exa research start \
  --instructions @examples/research_instructions.md \
  --schema @examples/research_schema.json \
  --model exa-research --pretty --save /tmp/research_start.json
ID=$(jq -r '.id // .taskId' /tmp/research_start.json)
exa research stream --id "$ID" | jq '.'
exa research get --id "$ID" --events --pretty | jq '.'
```

See also: `examples/research_stream_json.py`.

## Context (Exa Code) for RAG

```bash
exa context query --query "pandas groupby examples" --tokensNum 2048 --pretty --save /tmp/context.json
```

See also: `examples/context_rag_snippet.py`.
