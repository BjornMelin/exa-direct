"""Helpers for exposing workflows as OpenAI Responses function tools."""

# pylint: disable=duplicate-code

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .. import client
from ..workflows import registry

_ENABLED_VALUES = {"1", "true", "yes"}


def _ensure_openai_enabled() -> None:
    """Raise if OpenAI integrations are disabled."""
    if os.getenv("EXA_DIRECT_ENABLE_OPENAI", "0").lower() not in _ENABLED_VALUES:
        raise RuntimeError(
            "Set EXA_DIRECT_ENABLE_OPENAI=1 to enable OpenAI Responses integration."
        )


def _default_service_factory() -> client.ExaService:
    """Return a configured :class:`~exa_direct.client.ExaService` instance."""
    _ensure_openai_enabled()
    api_key = client.resolve_api_key(None)
    return client.create_service(api_key)


@dataclass
class WorkflowFunctionTool:
    """Container that mirrors Responses function tool metadata."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., dict[str, Any]]


def workflow_function_tool(
    name: str,
    *,
    service_factory: Callable[[], client.ExaService] | None = None,
) -> WorkflowFunctionTool:
    """Create a function-tool spec for the given workflow."""
    definition = registry.get(name)
    factory = service_factory or _default_service_factory
    if service_factory is None:
        _ensure_openai_enabled()

    def _handler(**kwargs: Any) -> dict[str, Any]:
        """Execute the named workflow with keyword arguments from Responses."""
        service = factory()
        try:
            inputs = definition.inputs_type(**kwargs)
            outputs = registry.execute(name, service, inputs)
            # Responses function tools expect compact payloads; we surface the
            # workflow outputs directly to keep contracts minimal.
            return outputs.model_dump(exclude_none=True)
        finally:
            closer = getattr(service, "close", None)
            if callable(closer):
                closer()

    # Return the function tool spec.
    return WorkflowFunctionTool(
        name=definition.name,
        description=definition.summary,
        parameters=definition.inputs_type.model_json_schema(),
        handler=_handler,
    )
