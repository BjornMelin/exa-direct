"""Tests for global CLI options behaviour."""

from __future__ import annotations

import pytest

from exa_direct import cli


def test_global_flags_parse_after_subcommand() -> None:
    """Global options should be accepted after the chosen command."""
    parser = cli.build_parser()
    args = parser.parse_args([
        "search",
        "--query",
        "synthetic data trends",
        "--pretty",
        "--api-key",
        "abc123",
    ])

    assert args.command == "search"
    assert args.query == "synthetic data trends"
    assert getattr(args, "pretty", False) is True
    assert args.api_key == "abc123"


def test_global_flags_default_absent_when_not_passed() -> None:
    """Global options should remain unset when omitted."""
    parser = cli.build_parser()
    args = parser.parse_args(["search", "--query", "vector databases"])

    assert not hasattr(args, "pretty")
    assert getattr(args, "save", None) is None
    assert getattr(args, "api_key", None) is None


def test_main_loads_dotenv_and_uses_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """`main` should load .env before resolving API keys."""
    called: dict[str, bool] = {}

    def _fake_load() -> None:
        called["dotenv"] = True

    monkeypatch.setattr(cli, "load_dotenv", _fake_load)
    monkeypatch.setattr(
        cli.structured_logging, "configure", lambda: None, raising=False
    )
    monkeypatch.setattr(cli.client, "resolve_api_key", lambda explicit: "resolved-key")
    monkeypatch.setattr(cli.client, "create_service", lambda key: object())
    monkeypatch.setattr(cli, "_dispatch", lambda service, args: {"ok": True})

    exit_code = cli.main(["search", "--query", "test"])

    assert exit_code == 0
    assert called.get("dotenv") is True
