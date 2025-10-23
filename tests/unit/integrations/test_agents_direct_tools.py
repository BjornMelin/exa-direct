"""Unit tests for direct Exa function tools exposed on the coordinator."""

from __future__ import annotations

import json
from typing import cast

import pytest

from exa_direct import client as client_module
from exa_direct._testing import StubService
from exa_direct.integrations import agents as agents_module

pytestmark = pytest.mark.unit


def test_coordinator_includes_direct_exa_tools(enable_openai: None) -> None:
    """Coordinator includes exa_* direct tools for chaining."""
    pytest.importorskip("agents")
    settings = agents_module.CoordinatorSettings(model="gpt-4.1-mini")
    coordinator, _ = agents_module.build_coordinator(settings=settings)
    assert coordinator.agent is not None
    names = {getattr(t, "name", None) for t in coordinator.agent.tools}
    assert {"exa_search", "exa_contents", "exa_answer"}.issubset(names)


def test_exa_search_tool_executes_with_stub(
    monkeypatch: pytest.MonkeyPatch, enable_openai: None
) -> None:
    """Direct exa_search tool resolves through service factory and returns payload."""
    pytest.importorskip("agents")
    monkeypatch.setenv("EXA_API_KEY", "stub")
    monkeypatch.setattr(
        agents_module.client, "resolve_api_key", lambda explicit: "stub"
    )

    created: list[StubService] = []

    def factory() -> client_module.ExaService:
        svc = StubService()
        created.append(svc)
        return cast(client_module.ExaService, svc)

    settings = agents_module.CoordinatorSettings(model="gpt-4.1-mini")
    coordinator, _ = agents_module.build_coordinator(
        settings=settings, service_factory=factory
    )

    # Find exa_search tool
    assert coordinator.agent is not None
    tool = next(
        t for t in coordinator.agent.tools if getattr(t, "name", None) == "exa_search"
    )

    from agents.tool_context import ToolContext  # type: ignore[import-not-found]

    ctx = ToolContext(
        context=None,  # type: ignore[arg-type]
        tool_name=getattr(tool, "name", "exa_search"),
        tool_call_id="call-1",
        tool_arguments=json.dumps({"query": "hello", "params": {"type": "fast"}}),
    )

    import asyncio

    async def _run():
        """Run the tool via its on_invoke_tool using a minimal ToolContext."""
        # type: ignore[attr-defined]
        result = await tool.on_invoke_tool(ctx, ctx.tool_arguments)
        assert result["query"] == "hello"
        assert result["params"]["type"] == "fast"

    asyncio.run(_run())
    assert created and created[0].close_calls == 0
