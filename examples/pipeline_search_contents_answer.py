"""End-to-end pipeline: search → contents → answer using the `exa` CLI.

This script shells out to the installed `exa` command and stitches together
three steps:

1) Search for a topic (fast type).
2) Fetch highlights (and optionally text) for the top results.
3) Ask a follow-up question with `exa answer`.

Usage:
  export EXA_API_KEY=sk-...
  python examples/pipeline_search_contents_answer.py --query "hybrid vector search"

"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections.abc import Sequence
from typing import Any


def run_exa(args: Sequence[str]) -> dict[str, Any]:
    """Run `exa` with args and parse stdout JSON."""
    env = {**os.environ, "EXA_API_KEY": os.environ.get("EXA_API_KEY", "")}
    proc = subprocess.run(
        ["exa", *args],
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(proc.stdout)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Search → contents → answer pipeline")
    parser.add_argument("--query", required=True, help="Topic to search/answer")
    parser.add_argument(
        "--num-results", type=int, default=5, help="How many search results to fetch"
    )
    parser.add_argument(
        "--include-text",
        action="store_true",
        help="Also fetch full text in contents (larger payload)",
    )
    args = parser.parse_args()

    # 1) Search (fast)
    search = run_exa(["search", "--query", args.query, "--type", "fast", "--pretty"])
    items = list(search.get("results") or search.get("data") or [])
    urls = [it.get("url") for it in items if it.get("url")][: args.num_results]
    print(f"Collected {len(urls)} URLs from search.")

    # 2) Contents (highlights, optional text)
    contents_args: list[str] = ["contents", *urls, "--highlights"]
    if args.include_text:
        contents_args.append("--text")
    contents = run_exa(contents_args)
    print(f"Contents fetched for {len(urls)} URLs.")

    # Optionally show first highlight snippet if present
    try:
        first = (contents.get("results") or contents.get("data") or [])[0]
        hl = first.get("highlights")
        if hl:
            print("First highlight:", hl[0][:200], "...")
    except Exception:  # noqa: BLE001 # pylint: disable=broad-exception-caught
        pass

    # 3) Answer (single-shot)
    answer = run_exa(["answer", "--query", f"Summarize: {args.query}", "--pretty"])
    print(json.dumps(answer, indent=2))


if __name__ == "__main__":
    main()
