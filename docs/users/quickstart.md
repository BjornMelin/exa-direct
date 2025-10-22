# Quickstart

This guide helps you install and use the exa-direct CLI quickly.

## Prerequisites

- Python 3.10+
- An Exa API key (from <https://dashboard.exa.ai/api-keys>)

## Install

```bash
python -m venv .venv && . .venv/bin/activate
pip install -U pip
pip install -e .
```

## Configure

```bash
export EXA_API_KEY=sk-...
```

You can also create a `.env` file containing any of the supported variables:
`EXA_API_KEY`, `OPENAI_API_KEY`, `EXA_DIRECT_ENABLE_OPENAI`. The CLI loads the
file automatically, so `--api-key` is optional for daily use and OpenAI helpers
pick up their credentials with no extra wiring.

## First Run

- Fast search with page text:

```bash
exa search --query "Latest research in LLMs" --type fast --text --pretty
```

- Contents (livecrawl preferred):

```bash
exa contents https://example.com --text --livecrawl preferred
```

- Answer with citations:

```bash
exa answer --query "Summarize Exa 2.0 updates" --pretty
```

- Research (create + poll):

```bash
exa research start --instructions @examples/research_instructions.md \
  --schema @examples/research_schema.json --model exa-research-fast
exa research poll --id <researchId> --preset balanced
```

- Research (stream JSON-lines):

```bash
exa research stream --id <researchId> | jq .
```

- Context (Exa Code):

```bash
exa context query --query "pandas groupby examples" --tokensNum dynamic
```

> Global flags (`--api-key`, `--pretty`, `--save`) can be placed either before
> or after the subcommand; the CLI normalises both forms.

### Transport notes (Context)

The Context client prefers HTTP/2 with a total timeout. Transient network
errors and HTTP 5xx responses are retried with short backoff (0.1s, 0.2s,
0.5s) before a final attempt, and the transport downgrades to HTTP/1.1
automatically when HTTP/2 support is unavailable.

## References

- **API overview:** <https://exa.ai/blog/exa-api-2-0>
- **Endpoints:**
  - **Search:** <https://docs.exa.ai/reference/search>
  - **Contents:** <https://docs.exa.ai/reference/get-contents>
  - **Find Similar:** <https://docs.exa.ai/reference/find-similar-links>
  - **Answer:** <https://docs.exa.ai/reference/answer>
  - **Research:**
    - **Create:** <https://docs.exa.ai/reference/research/create-a-task>
    - **Get:** <https://docs.exa.ai/reference/research/get-a-task>
    - **List:** <https://docs.exa.ai/reference/research/list-tasks>
  - **Context (Exa Code):** <https://docs.exa.ai/reference/context>
  - **Livecrawling Contents:** <https://docs.exa.ai/reference/livecrawling-contents>
