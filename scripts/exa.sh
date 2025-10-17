#!/usr/bin/env bash
# Simple helpers for direct Exa API calls.
# Usage: source this file or call functions with EXA_API_KEY set.

set -euo pipefail

require_key() {
  if [[ -z "${EXA_API_KEY:-}" ]]; then
    echo "EXA_API_KEY is not set" >&2
    exit 1
  fi
}

exa_search() {
  require_key
  local query="$1"
  shift || true
  curl -sS -X POST "https://api.exa.ai/search" \
    -H "x-api-key: ${EXA_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"query\":$(printf '%s' "${query}" | jq -Rs .),\"text\":true}"
}

exa_contents() {
  require_key
  local url="$1"
  curl -sS -X POST "https://api.exa.ai/contents" \
    -H "x-api-key: ${EXA_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"urls\":[$(printf '%s' "${url}" | jq -Rs .)],\"text\":true,\"livecrawl\":\"preferred\"}"
}

exa_answer() {
  require_key
  local query="$1"
  curl -sS -X POST "https://api.exa.ai/answer" \
    -H "x-api-key: ${EXA_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"query\":$(printf '%s' "${query}" | jq -Rs .)}"
}

exa_find_similar() {
  require_key
  local url="$1"
  curl -sS -X POST "https://api.exa.ai/findSimilar" \
    -H "x-api-key: ${EXA_API_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"url\":$(printf '%s' "${url}" | jq -Rs .),\"text\":true}"
}

exa_research_start() {
  require_key
  local body_file="$1"
  curl -sS -X POST "https://api.exa.ai/research/v1/research/v1" \
    -H "Content-Type: application/json" \
    -d @"${body_file}"
}

exa_research_get() {
  require_key
  local research_id="$1"
  curl -sS "https://api.exa.ai/research/v1/research/v1/${research_id}"
}

exa_research_stream() {
  require_key
  local research_id="$1"
  curl -sS -N -H "Accept: text/event-stream" \
    "https://api.exa.ai/research/v1/research/v1/${research_id}?stream=true"
}

exa_research_list() {
  require_key
  local limit="${1:-10}"
  curl -sS "https://api.exa.ai/research/v1/research/v1?limit=${limit}"
}

