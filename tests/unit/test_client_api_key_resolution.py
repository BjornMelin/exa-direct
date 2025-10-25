"""Tests for API key resolution precedence, including .env support."""

from __future__ import annotations

from pathlib import Path

import pytest
from dotenv import load_dotenv as _real_load_dotenv

from exa_direct import client as client_module


@pytest.fixture(autouse=True)
def _reset_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure tests start without EXA_API_KEY in the environment."""
    monkeypatch.delenv("EXA_API_KEY", raising=False)


def test_resolve_api_key_prefers_cli_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """Explicit CLI flag should take precedence over environment values."""
    monkeypatch.setenv("EXA_API_KEY", "env-key")
    result = client_module.resolve_api_key("cli-key")
    assert result == "cli-key"


def test_resolve_api_key_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment variable should be used when no CLI flag is provided."""
    monkeypatch.setenv("EXA_API_KEY", "env-key")
    result = client_module.resolve_api_key(None)
    assert result == "env-key"


def test_resolve_api_key_loads_dotenv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`.env` file should be consulted when the environment lacks the key."""
    dotenv = tmp_path / ".env"
    dotenv.write_text("EXA_API_KEY=dot-env-key\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        client_module,
        "load_dotenv",
        lambda: _real_load_dotenv(dotenv_path=dotenv, override=True),
    )
    result = client_module.resolve_api_key(None)
    assert result == "dot-env-key"


def test_resolve_api_key_raises_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """An informative error should be raised when no key can be resolved."""
    monkeypatch.setattr(client_module, "load_dotenv", lambda: False)
    with pytest.raises(RuntimeError) as exc:
        client_module.resolve_api_key(None)
    assert "EXA_API_KEY is required" in str(exc.value)
