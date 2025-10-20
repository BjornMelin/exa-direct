"""Unit tests for the workflow CLI command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from exa_direct import cli
from exa_direct._testing import StubService

pytestmark = pytest.mark.unit


def test_workflow_run_invokes_registry(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    stub_service_type: type[StubService],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`workflow run` executes through the registry and prints JSON."""
    payload = {
        "query": "cli",
        "search_params": {"num_results": 1},
        "contents_params": {},
    }
    payload_path = tmp_path / "input.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    service = stub_service_type()

    monkeypatch.setenv("EXA_API_KEY", "stub")
    monkeypatch.setattr(cli.client, "resolve_api_key", lambda explicit: "stub")
    monkeypatch.setattr(cli.client, "create_service", lambda api_key: service)

    exit_code = cli.main([
        "workflow",
        "run",
        "search_cli",
        "--input",
        f"@{payload_path}",
    ])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["workflow"] == "search_cli"
    assert output["outputs"]["results"]["query"] == "cli"
    assert service.search_calls
