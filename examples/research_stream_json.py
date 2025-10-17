"""Start a research task and stream JSON events until completion.

This example uses the CLI's JSON-lines streaming for research tasks and
aggregates the final snapshot when a `completed` event appears.

Usage:
  export EXA_API_KEY=sk-...
  python examples/research_stream_json.py \
      --instructions examples/research_instructions.md \
      --schema examples/research_schema.json \
      --model exa-research
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections.abc import Iterable
from typing import Any


def run_json(cmd: list[str]) -> dict[str, Any]:
    """Execute the `exa` CLI with arguments and return parsed JSON."""
    env = {**os.environ, "EXA_API_KEY": os.environ.get("EXA_API_KEY", "")}
    proc = subprocess.run(cmd, env=env, check=True, text=True, capture_output=True)
    return json.loads(proc.stdout)


def iter_json_lines(cmd: list[str]) -> Iterable[dict[str, Any]]:
    """Iterate over JSON-lines from the `exa` CLI."""
    env = {**os.environ, "EXA_API_KEY": os.environ.get("EXA_API_KEY", "")}
    with subprocess.Popen(
        cmd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as proc:
        assert proc.stdout is not None
        for line in proc.stdout:
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Research stream (JSON-lines)")
    parser.add_argument("--instructions", required=True, help="Path to instructions")
    parser.add_argument("--schema", required=True, help="Path to JSON Schema")
    parser.add_argument(
        "--model",
        default="exa-research",
        choices=["exa-research-fast", "exa-research", "exa-research-pro"],
    )
    args = parser.parse_args()

    start = run_json([
        "exa",
        "research",
        "start",
        "--instructions",
        f"@{args.instructions}",
        "--schema",
        f"@{args.schema}",
        "--model",
        args.model,
    ])

    task_id = start.get("id") or start.get("taskId")
    if not task_id:
        raise SystemExit(f"No task id in start response: {start}")

    print(f"Streaming events for task: {task_id}")
    final_snapshot: dict[str, Any] | None = None
    for event in iter_json_lines(["exa", "research", "stream", "--id", str(task_id)]):
        etype = event.get("event") or event.get("type")
        if etype:
            print("event:", etype)
        if event.get("status") == "completed" or etype == "completed":
            final_snapshot = event
            break

    if final_snapshot is None:
        print("No completion event captured; falling back to GET ...")
        final_snapshot = run_json(["exa", "research", "get", "--id", str(task_id)])

    print(json.dumps(final_snapshot, indent=2))


if __name__ == "__main__":
    main()
