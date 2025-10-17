#!/usr/bin/env bash
set -euo pipefail

URL="https://arxiv.org/abs/2307.06435"

echo "== Basic find-similar =="
exa find-similar --url "$URL" --num-results 5 --pretty

echo "\n== Find-similar with filters and inline contents =="
exa find-similar --url "$URL" \
  --exclude-source-domain \
  --include-domains arxiv.org \
  --start-published-date 2024-01-01 \
  --text --highlights --summary-query "main findings" \
  --livecrawl auto --pretty
