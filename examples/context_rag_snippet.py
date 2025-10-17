"""Fetch code-focused context with `exa context` for RAG prompts.

This example queries Exa Code's Context API via the CLI and prints a
token-efficient snippet suitable for passing to an LLM as system/user
context. It avoids any external LLM dependencies.

Usage:
  export EXA_API_KEY=sk-...
  python examples/context_rag_snippet.py --query "pandas groupby examples" --tokens 2048
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from typing import Any


def run_exa(cmd: list[str]) -> dict[str, Any]:
    """Execute the `exa` CLI with arguments and return parsed JSON."""
    env = {**os.environ, "EXA_API_KEY": os.environ.get("EXA_API_KEY", "")}
    proc = subprocess.run(cmd, env=env, check=True, text=True, capture_output=True)
    return json.loads(proc.stdout)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Get code context for RAG prompts")
    parser.add_argument("--query", required=True, help="Context query text")
    parser.add_argument(
        "--tokens",
        default="dynamic",
        help="Token budget (integer) or 'dynamic'",
    )
    args = parser.parse_args()

    payload = run_exa([
        "exa",
        "context",
        "query",
        "--query",
        args.query,
        "--tokensNum",
        str(args.tokens),
    ])
    # Print the main context field if present, else the whole payload.
    context_text = payload.get("context") or payload.get("content") or ""
    if context_text:
        print(context_text)
    else:
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
