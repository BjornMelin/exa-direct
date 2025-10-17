#!/usr/bin/env bash
set -euo pipefail

# Examples for `exa contents`

URL1="https://example.com"
URL2="https://www.wikipedia.org/"

echo "== Fetch text and highlights with livecrawl preferred =="
exa contents "$URL1" "$URL2" --text --highlights --livecrawl preferred --pretty

echo "\n== Fetch with metadata and filter-empty-results =="
exa contents "$URL1" --metadata --filter-empty-results --pretty

echo "\n== Summary with schema and subpages targeting =="
tmp_schema=$(mktemp)
cat >"$tmp_schema" <<'JSON'
{"type":"object","properties":{"summary":{"type":"string"}},"required":["summary"]}
JSON

exa contents "$URL1" --summary-schema "$tmp_schema" --subpages 1 --subpage-target sources --pretty
rm -f "$tmp_schema"
