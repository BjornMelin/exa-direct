#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <researchId> [--api-key KEY]" >&2
  exit 1
fi

rid="$1"; shift || true

if command -v jq >/dev/null 2>&1; then
  exa research stream --id "$rid" --json-events "$@" | jq .
else
  # Fallback to Python pretty printer if jq is unavailable
  exa research stream --id "$rid" --json-events "$@" | python -m json.tool
fi
