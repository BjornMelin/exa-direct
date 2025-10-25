"""Unit tests for the `exa agents run` CLI surface."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pytest

from exa_direct import cli

pytestmark = pytest.mark.unit


@dataclass
class _StubRunResult:
    final_output: Any


def test_agents_run_happy_path(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    """`exa agents run` prints final_output JSON and returns 0."""
    monkeypatch.setenv("EXA_DIRECT_ENABLE_OPENAI", "1")
    monkeypatch.setenv("EXA_API_KEY", "stub")

    # Ensure agents package is present; skip if not
    pytest.importorskip("agents")

    # Patch Runner path used by our integration to avoid real LLM calls
    from exa_direct.integrations import agents as agents_module

    async def _fake_run_coordinator(*_a, **_kw):  # type: ignore[no-untyped-def]
        """Fake run_coordinator that returns a stub result."""
        import asyncio

        await asyncio.sleep(0)
        return _StubRunResult("ok")

    monkeypatch.setattr(agents_module, "run_coordinator", _fake_run_coordinator)

    exit_code = cli.main(
        ["agents", "run", "--input", "hello world"]  # type: ignore[arg-type]
    )
    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["final_output"] == "ok"


def test_agents_run_requires_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fails with helpful message when OpenAI integration disabled."""
    monkeypatch.delenv("EXA_DIRECT_ENABLE_OPENAI", raising=False)
    monkeypatch.setenv("EXA_API_KEY", "stub")
    exit_code = cli.main(
        ["agents", "run", "--input", "hello"]  # type: ignore[arg-type]
    )
    assert exit_code == 1
