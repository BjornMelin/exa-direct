#!/usr/bin/env bash
set -euo pipefail

echo "== Context (Exa Code) query with dynamic tokensNum =="
exa context query --query "pandas groupby examples" --tokensNum dynamic | jq .

echo "\n== Context with integer tokensNum =="
exa context query --query "fastapi background tasks" --tokensNum 2000 | jq .
