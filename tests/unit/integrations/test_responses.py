"""Unit tests for the Responses integration helper."""

from __future__ import annotations

from typing import cast

import pytest

from exa_direct import client as client_module
from exa_direct._testing import StubService
from exa_direct.integrations.responses import workflow_function_tool
from exa_direct.workflows import registry

pytestmark = pytest.mark.unit


def test_responses_function_tool_executes_workflow(
    enable_openai: None,
    stub_service_type: type[StubService],
) -> None:
    """Function-tool handler executes workflows and closes the service."""
    definition = registry.get("answer_cli")

    created: list[StubService] = []

    def factory() -> client_module.ExaService:
        service = stub_service_type()
        created.append(service)
        return cast(client_module.ExaService, service)

    tool = workflow_function_tool(definition.name, service_factory=factory)
    result = tool.handler(query="hello", options={"include_text": True})

    service = created[0]
    assert result["answer"]["query"] == "hello"
    assert result["answer"]["options"]["include_text"] is True
    assert service.close_calls == 1


def test_responses_requires_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Attempting to create a tool without the toggle should fail."""
    monkeypatch.delenv("EXA_DIRECT_ENABLE_OPENAI", raising=False)
    with pytest.raises(RuntimeError):
        workflow_function_tool("search_cli")
