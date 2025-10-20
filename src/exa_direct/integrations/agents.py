"""Helpers for wrapping workflows as OpenAI Agents SDK tools."""

# pylint: disable=duplicate-code

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from agents import function_tool

from .. import client
from ..workflows import registry


def _default_service_factory() -> client.ExaService:
    """Return a configured :class:`~exa_direct.client.ExaService` instance."""
    if os.getenv("EXA_DIRECT_ENABLE_OPENAI", "0").lower() not in {"1", "true", "yes"}:
        raise RuntimeError(
            "Set EXA_DIRECT_ENABLE_OPENAI=1 to enable OpenAI Agents integration."
        )
    api_key = client.resolve_api_key(None)
    return client.create_service(api_key)


def workflow_tool(
    name: str,
    *,
    service_factory: Callable[[], client.ExaService] | None = None,
):
    """Return a function_tool-wrapped callable for a workflow."""
    definition = registry.get(name)
    factory = service_factory or _default_service_factory

    @function_tool(
        name_override=definition.name, description_override=definition.summary
    )
    def _tool(**kwargs: Any) -> dict[str, Any]:
        """Execute the named workflow with keyword arguments from Agents SDK."""
        service = factory()
        try:
            inputs = definition.inputs_type(**kwargs)
            outputs = registry.execute(name, service, inputs)
            return outputs.model_dump(exclude_none=True)
        finally:
            closer = getattr(service, "close", None)
            if callable(closer):
                closer()

    return _tool
