#!/usr/bin/env bash
set -euo pipefail

echo "== Basic answer with citations =="
exa answer --query "What is the latest valuation of SpaceX?" --include-text --pretty

echo "\n== Structured answer with schema and model selection =="
tmp_schema=$(mktemp)
cat >"$tmp_schema" <<'JSON'
{"type":"object","properties":{"value":{"type":"string"},"sources":{"type":"array","items":{"type":"string"}}},"required":["value","sources"]}
JSON

exa answer --query "Summarize the 3 biggest open challenges in RL" \
  --model exa-pro --output-schema "$tmp_schema" --pretty

rm -f "$tmp_schema"

echo "\n== Streamed answer as JSON-lines (chunk events) =="
exa answer --query "Name three popular vector databases" --stream --json-lines
