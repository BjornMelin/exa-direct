# Code Reviews & Analysis

This document summarizes automated analyses (Zen tools) performed on `src/` as of 2025‑10‑17.

## Summary

- Architecture: minimal CLI (`argparse`) dispatching to a thin service (`ExaService`) that blends `exa_py`
  SDK with direct REST calls where needed (e.g., contents, research stream/get).
- Quality: typed, Google‑style docstrings, lint/type/test gates are green. Streaming output behavior is intentional.

## Findings (No code changes required)

- CLI dispatcher complexity is acceptable today; if the command surface grows, consider splitting
  handlers per command to reduce branching.
- Validate periodically that the research REST path remains correct against the Exa docs.
- Streaming UX: default prints raw SSE lines; JSON‑per‑event output is available via `--json-events`.
- File import placement and exception granularity are acceptable given CLI startup goals;
  adjust only if we tighten lint in the future.

## Recommendations to Document (not code changes)

- Keep AGENTS.md updated with polling presets (fast=10s, exa‑research=30s, pro=40s) and SSE notes.
- Provide integration examples that shell out to `exa` and parse JSON (see examples/agents_python.py).
- Capture best‑practices in a user‑facing page (done: user/best_practices.md) and link from the docs index.
