#!/usr/bin/env bash
set -euo pipefail

# Examples for `exa search` variations

echo "== Fast search with type=fast =="
exa search --query "2025 LLM agent benchmarks" --type fast --pretty

echo "\n== Neural search with include/exclude domains and date filters =="
exa search --query "vector db hybrid search" \
  --type neural \
  --include-domains qdrant.tech milvus.io \
  --exclude-domains reddit.com \
  --start-published-date 2025-01-01 \
  --end-published-date 2025-12-31 --pretty

echo "\n== Auto search with autoprompt, category, moderation, flags =="
exa search --query "recent transformer training optimizations" \
  --type auto --use-autoprompt \
  --category news --moderation \
  --flags experimentalA experimentalB --pretty

echo "\n== Search with inline contents (text+highlights+summary) =="
tmp_schema=$(mktemp)
cat >"$tmp_schema" <<'JSON'
{"type":"object","properties":{"bulletPoints":{"type":"array","items":{"type":"string"}}},"required":["bulletPoints"]}
JSON

exa search --query "state of AGI in 2025" \
  --text --highlights --summary-query "key takeaways" --summary-schema "$tmp_schema" \
  --livecrawl auto --subpages 1 --subpage-target sources --pretty

rm -f "$tmp_schema"
