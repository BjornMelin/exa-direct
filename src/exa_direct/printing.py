"""Helpers for writing JSON output to stdout or files."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def print_json(data: Any, *, pretty: bool = False) -> None:
    """Print JSON data to stdout.

    Args:
        data: Any JSON-serializable value.
        pretty: Whether to indent output for readability.
    """
    if pretty:
        sys.stdout.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(
            json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
        )


def save_json(path: str, data: Any, *, pretty: bool = True) -> None:
    """Persist JSON data to disk.

    Args:
        path: Output file path.
        data: Any JSON-serializable value.
        pretty: Whether to indent output for readability.
    """
    target = Path(path)
    if pretty:
        payload = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    target.write_text(payload + "\n", encoding="utf-8")
