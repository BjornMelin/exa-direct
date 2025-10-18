# Integration Recipes

Concise, copy‑paste workflows for integrating the `exa` CLI into agent and automation pipelines.
All commands print JSON to stdout; add `--pretty` for readability and `--save path.json` to persist.

## 1) Agent Shell‑Out Pattern (Python)

```python
import json, os, subprocess

def run_exa(args: list[str]) -> dict:
    env = {**os.environ, "EXA_API_KEY": os.environ.get("EXA_API_KEY", "")}
    out = subprocess.check_output(["exa", *args], env=env, text=True)
    return json.loads(out)

# Example: fast search
res = run_exa(["search", "--query", "hybrid vector search", "--type", "fast"]) 
```

See also: `examples/agents_python.py`.

## 2) Search → Contents (Highlights/Text) → Answer

```bash
exa search --query "hybrid vector search" --type fast --pretty --save /tmp/search.json
URL1=$(jq -r '.results[0].url // .data[0].url' /tmp/search.json)
URL2=$(jq -r '.results[1].url // .data[1].url' /tmp/search.json)
exa contents "$URL1" "$URL2" --highlights --pretty --save /tmp/contents.json
exa answer --query "Summarize hybrid vector search" --pretty
```

See also: `examples/pipeline_search_contents_answer.py`.

## 3) Research (Start → Stream JSON‑Lines → Final Snapshot)

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

## 4) Polling with UX Presets

```bash
# CLI preset hints: fast=10s, balanced=30s, pro=40s; the SDK retains its own default intervals unless you override them.
exa research poll --id "$ID" --preset balanced --pretty
```

## 5) Context (Exa Code) for RAG

```bash
exa context query --query "pandas groupby examples" --tokensNum 2048 --pretty --save /tmp/context.json
```

See also: `examples/context_rag_snippet.py`.

## 6) Process‑Level Timeout (Wrapper)

```bash
# Linux/macOS example: kill if stream exceeds 15 minutes
timeout 15m sh -c 'exa research stream --id "$ID" > /tmp/stream.jsonl'
```
