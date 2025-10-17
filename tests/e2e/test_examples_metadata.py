"""E2E metadata checks for example scripts without network calls.

Ensures files exist, are executable, and have a shebang.
"""

from __future__ import annotations

from pathlib import Path


def _check_script(path: Path) -> None:
    assert path.exists(), f"Missing example: {path}"
    text = path.read_text(encoding="utf-8")
    assert text.startswith("#!/"), f"Missing shebang in {path}"


def test_examples_present_and_executable() -> None:
    """Ensure example scripts exist and have a shebang."""
    root = Path("examples")
    scripts = [
        root / "search_examples.sh",
        root / "contents_examples.sh",
        root / "find_similar_examples.sh",
        root / "answer_examples.sh",
        root / "research_examples.sh",
        root / "context_example.sh",
        root / "stream_consumer.sh",
    ]
    for script in scripts:
        _check_script(script)
