"""Agent-side helpers to call the `exa` CLI.

This example shows how to shell out to the installed `exa` command
from a Python agent or tool and parse JSON responses. Ensure the
`EXA_API_KEY` environment variable is set and that `exa` is on PATH
(installed via `pip install -e .`).

Run:
  python examples/agents_python.py

"""

from __future__ import annotations

import json
import os
import subprocess
from collections.abc import Sequence
from typing import Any


def run_exa(args: Sequence[str]) -> dict[str, Any]:
    """Execute the `exa` CLI with arguments and return parsed JSON.

    Args:
      args: Command arguments to pass after the `exa` executable.

    Returns:
      Parsed JSON object from stdout.

    Raises:
      CalledProcessError: If the `exa` command fails (non-zero exit).
      JSONDecodeError: If stdout is not valid JSON.
    """
    env = {**os.environ, "EXA_API_KEY": os.environ.get("EXA_API_KEY", "")}
    proc = subprocess.run(
        ["exa", *args],
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(proc.stdout)


def exa_search(query: str, type_: str = "fast") -> dict[str, Any]:
    """Run an Exa search with a specific search type.

    Args:
      query: Search query text.
      type_: One of {"fast","auto","neural","keyword"}.

    Returns:
      Search API JSON result.
    """
    return run_exa(["search", "--query", query, "--type", type_])


def exa_research(
    instructions_path: str,
    schema_path: str,
    model: str = "exa-research",
) -> dict[str, Any]:
    """Create and poll a research task until completion.

    Args:
      instructions_path: Path to a text/markdown file with instructions.
      schema_path: Path to a JSON Schema file guiding the output.
      model: Research model (e.g., "exa-research-fast", "exa-research",
        "exa-research-pro").

    Returns:
      Completed research task payload.
    """
    start = run_exa([
        "research",
        "start",
        "--instructions",
        f"@{instructions_path}",
        "--schema",
        f"@{schema_path}",
        "--model",
        model,
    ])
    task_id = start.get("id") or start.get("taskId")
    if not task_id:
        raise RuntimeError(f"No task id in start response: {start}")
    return run_exa(["research", "poll", "--id", task_id, "--model", model])


def _ensure_api_key() -> str:
    """Return the API key or exit with a clear message."""
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        raise SystemExit("EXA_API_KEY not set. Export it or pass --api-key to the CLI.")
    return api_key


if __name__ == "__main__":
    _ensure_api_key()
    print(json.dumps(exa_search("hybrid search vector databases"), indent=2))
