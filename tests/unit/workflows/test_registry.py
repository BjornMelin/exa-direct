"""Unit tests for workflow registry behaviour."""

from __future__ import annotations

import pytest

from exa_direct._testing import StubService
from exa_direct.workflows import registry

pytestmark = pytest.mark.unit


def test_search_cli_workflow_executes_with_stub_service(
    stub_service_type: type[StubService],
) -> None:
    """Registry executes the search workflow and records service usage."""
    definition = registry.get("search_cli")
    inputs = definition.inputs_type(
        query="test query",
        search_params={"num_results": 5},
        contents_params={},
    )
    service = stub_service_type()

    outputs = registry.execute("search_cli", service, inputs)

    assert outputs.results["query"] == "test query"
    assert outputs.results["params"]["num_results"] == 5
    assert service.search_calls == [("test query", {"num_results": 5})]
