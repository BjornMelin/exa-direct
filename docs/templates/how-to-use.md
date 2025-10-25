# How to Use the AGENTS Template

This guide explains how to add `exa-direct` agent instructions into your environment
so AI coding agents execute the `exa` CLI reliably.

## 1) Prepare Environment

- Ensure you have an Exa API key and export it:

```
export EXA_API_KEY=sk-exa-...
```

- Optional: Create a `.env` file in your repo with `EXA_API_KEY` for local runs.

## 2) Copy the Template

Open `docs/templates/AGENTS_TEMPLATE.md` and copy its full contents into one of:

- Global `AGENTS.md` (applies to all repos for your agent tooling)
- Project-level `AGENTS.md` (applies only to this repo)
- Claude Code users can paste into `CLAUDE.md`
- Gemini CLI users can paste into their project agent guide file (same content)

Tip: Keep a short project-specific preface above the template to record domain context, default flags,
and workflow names used most often.

## 3) Validate CLI Reachability

Run a quick dry check to confirm the CLI is on `PATH` and the key is set:

```
exa workflow list --pretty
```

If this prints JSON with workflow names, your integration is ready.

## 4) Agent Integration Hints

- Codex CLI (GPT‑5‑Codex / gpt‑5):
  - Use `workflow describe <name> --schema` to discover input/output shapes.
  - Prefer `workflow run` with `--param` or `--input @file.json` for typed calls.
- Claude Code (`CLAUDE.md`):
  - Treat `exa` as a deterministic tool. Capture stdout JSON and avoid `--pretty` during automated steps.
- Gemini CLI:
  - For long research tasks, use `research stream` and aggregate JSON-lines until completion.

## 5) Common Patterns

- Human-readable logs: add `--pretty`.
- Persist outputs: use `--save out.json`.
- Streaming:
  - `exa answer --stream --json-lines` emits one JSON object per line.
  - `exa research stream` always emits JSON-lines.

## 6) Troubleshooting

- Missing API key: set `EXA_API_KEY` or use `--api-key`.
- Malformed JSON schema paths: prefix with `@` (e.g., `--summary-schema @schema.json`).
- Parameter mistakes with workflows: use `exa workflow describe <name> --schema` and match field names exactly.

## 7) Keep It Updated

When `exa-direct` updates its CLI surface or workflows, re-copy `AGENTS_TEMPLATE.md`
so your global/project `AGENTS.md` stays current.
