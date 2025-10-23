# pyright: reportGeneralTypeIssues=false, reportMissingImports=false
"""Unit tests for Agents SDK integration helpers."""

from __future__ import annotations

from typing import cast

import pytest

from exa_direct import client as client_module
from exa_direct._testing import StubService
from exa_direct.integrations import agents as agents_module

pytestmark = pytest.mark.unit


def test_build_coordinator_returns_agents(
    enable_openai: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Coordinator exposes all workflows and returns specialists."""
    _ = pytest.importorskip("agents")
    monkeypatch.setenv("EXA_API_KEY", "stub")
    monkeypatch.setattr(
        agents_module.client, "resolve_api_key", lambda explicit: "stub"
    )
    monkeypatch.setattr(
        agents_module.client,
        "create_service",
        lambda key: cast(client_module.ExaService, StubService()),
    )
    settings = agents_module.CoordinatorSettings(model="gpt-4.1-mini")
    coordinator, specialists = agents_module.build_coordinator(settings=settings)
    assert coordinator.name == "workflow-orchestrator"
    assert specialists
    catalog = {spec.name for spec in specialists}
    registered = {wf.name for wf in agents_module.registry.list()}
    assert catalog == registered
    for spec in specialists:
        assert spec.agent is not None
        assert spec.tool_name.startswith("workflow_")
    assert "Responsibilities" in coordinator.instructions


def test_list_workflow_specialists(enable_openai: None) -> None:
    """Specialist helper yields descriptors even without coordinator."""
    pytest.importorskip("agents")
    specialists = agents_module.list_workflow_specialists()
    names = {spec.name for spec in specialists}
    assert names == {wf.name for wf in agents_module.registry.list()}


def test_specialist_executes_workflow(
    monkeypatch: pytest.MonkeyPatch, enable_openai: None
) -> None:
    """Specialist tool executes workflow when invoked (no asyncio plugin needed)."""
    import asyncio

    pytest.importorskip("agents")
    monkeypatch.setenv("EXA_API_KEY", "stub")
    monkeypatch.setattr(
        agents_module.client, "resolve_api_key", lambda explicit: "stub"
    )
    settings = agents_module.CoordinatorSettings(model="gpt-4.1-mini")

    created: list[StubService] = []

    def factory() -> client_module.ExaService:
        service = StubService()
        created.append(service)
        return cast(client_module.ExaService, service)

    _coordinator, specialists = agents_module.build_coordinator(
        settings=settings,
        service_factory=factory,
    )
    specialist = next(spec for spec in specialists if spec.name == "answer_cli")
    tool = specialist.agent.tools[0]  # type: ignore[index]

    async def _run() -> None:
        import json as _json

        from agents.tool_context import ToolContext  # type: ignore[import-not-found]

        # Invoke the tool via its on_invoke_tool using a minimal ToolContext.
        ctx = ToolContext(
            context=None,  # type: ignore[arg-type]
            tool_name=getattr(tool, "name", "workflow_answer_cli"),
            tool_call_id="test_call",
            tool_arguments=_json.dumps({"kwargs": {"query": "hello", "options": {}}}),
        )
        result = await tool.on_invoke_tool(
            ctx,
            ctx.tool_arguments,  # type: ignore[attr-defined]
        )
        assert "answer" in result or isinstance(result, dict)

    asyncio.run(_run())
    if created:
        assert created[0].close_calls == 0


def test_coordinator_has_all_specialist_tools(enable_openai: None) -> None:
    """Coordinator agent includes one tool per workflow specialist."""
    pytest.importorskip("agents")
    settings = agents_module.CoordinatorSettings(model="gpt-4.1-mini")
    coordinator, specialists = agents_module.build_coordinator(settings=settings)
    assert coordinator.agent is not None
    tool_names = {getattr(t, "name", None) for t in coordinator.agent.tools}
    # All specialist tools should be present on the coordinator (as_tool names)
    expected = {spec.tool_name for spec in specialists}
    assert expected.issubset(tool_names)
