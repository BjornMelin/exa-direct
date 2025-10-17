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
exa research poll --id <researchId> --model exa-research
```

-- Research (stream JSON-lines):

```bash
exa research stream --id <researchId> | jq .
```

- Context (Exa Code):

```bash
exa context query --query "pandas groupby examples" --tokensNum dynamic
```


## References

- API overview: <https://exa.ai/blog/exa-api-2-0>
- Search: <https://docs.exa.ai/reference/search>
- Contents: <https://docs.exa.ai/reference/get-contents>
- Find Similar: <https://docs.exa.ai/reference/find-similar-links>
- Answer: <https://docs.exa.ai/reference/answer>
- Research (Create/Get/List):
  - <https://docs.exa.ai/reference/research/create-a-task>
  - <https://docs.exa.ai/reference/research/get-a-task>
  - <https://docs.exa.ai/reference/research/list-tasks>
- Context (Exa Code): <https://docs.exa.ai/reference/context>
- How Exa Search Works: <https://docs.exa.ai/reference/how-exa-search-works>
- Livecrawling: <https://docs.exa.ai/reference/livecrawling-contents>
