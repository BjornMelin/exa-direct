"""CLI tests for workflow describe/list subcommands."""

from __future__ import annotations

import json

import pytest

from exa_direct import cli

pytestmark = pytest.mark.unit


def test_workflow_describe_with_schema(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`workflow describe --schema` returns JSON with schemas and plan."""
    monkeypatch.setenv("EXA_API_KEY", "stub")
    monkeypatch.setattr(cli.client, "resolve_api_key", lambda explicit: "stub")
    monkeypatch.setattr(cli.client, "create_service", lambda api_key: None)

    exit_code = cli.main(["workflow", "describe", "search_cli", "--schema"])
    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["name"] == "search_cli"
    assert "input_schema" in output
    assert "output_schema" in output
    assert "plan" in output


def test_workflow_list_table(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`workflow list --format table` prints human readable entries."""
    monkeypatch.setenv("EXA_API_KEY", "stub")
    monkeypatch.setattr(cli.client, "resolve_api_key", lambda explicit: "stub")
    monkeypatch.setattr(cli.client, "create_service", lambda api_key: None)

    exit_code = cli.main(["workflow", "list", "--format", "table"])
    assert exit_code == 0
    output = capsys.readouterr().out
    assert "search_cli" in output
