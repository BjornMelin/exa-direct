#!/usr/bin/env bash
set -euo pipefail

INSTR="examples/research_instructions.md"
SCHEMA="examples/research_schema.json"

echo "== Start research (schema + model) =="
start=$(exa research start --instructions "@$INSTR" --schema "@$SCHEMA" --model exa-research-fast)
echo "$start" | jq .

rid=$(echo "$start" | jq -r '.id // .researchId // .taskId')
if [[ -z "$rid" || "$rid" == "null" ]]; then
  echo "Failed to extract research id" >&2; exit 1
fi

echo "\n== Poll until finished (SDK defaults) =="
exa research poll --id "$rid" --pretty

echo "\n== Stream events (JSON-lines) =="
exa research stream --id "$rid" | jq .

echo "\n== Get with events =="
exa research get --id "$rid" --events --pretty

echo "\n== List last few tasks =="
exa research list --limit 5 --pretty
