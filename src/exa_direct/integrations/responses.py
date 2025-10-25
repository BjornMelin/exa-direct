"""Helpers for exposing workflows as OpenAI Responses function tools."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from .. import client, structured_logging
from ..workflows import registry

_ENABLED_VALUES = {"1", "true", "yes"}
_CACHE_DEFAULT = os.getenv("EXA_DIRECT_RESPONSES_CACHE", "1").lower() not in {
    "0",
    "false",
    "no",
}
_REQUIRE_APPROVAL = os.getenv("EXA_DIRECT_RESPONSES_REQUIRE_APPROVAL", "0").lower() in {
    "1",
    "true",
    "yes",
}


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


@dataclass(slots=True)
class WorkflowFunctionTool:
    """Container that mirrors Responses function tool metadata."""

    name: str
    description: str
    parameters: dict[str, Any]
    response: dict[str, Any]
    metadata: dict[str, Any]
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
    log = structured_logging.get_logger("exa_direct.responses")

    def _handler(**kwargs: Any) -> dict[str, Any]:
        """Execute the named workflow with keyword arguments from Responses."""
        payload = structured_logging.redact_payload(kwargs)
        log.info("responses.tool.start", workflow=name, inputs=payload)
        service = factory()
        try:
            inputs = definition.inputs_type(**kwargs)
            outputs = registry.execute(name, service, inputs)
            result = structured_logging.redact_payload(
                outputs.model_dump(exclude_none=True)
            )
            log.info("responses.tool.succeeded", workflow=name, outputs=result)
            return result
        except Exception as exc:  # pylint: disable=broad-except
            log.exception(
                "responses.tool.failed",
                workflow=name,
                error_type=type(exc).__name__,
                message=str(exc),
            )
            raise
        finally:
            closer = getattr(service, "close", None)
            if callable(closer):
                closer()

    return WorkflowFunctionTool(
        name=definition.name,
        description=definition.summary,
        parameters=definition.inputs_type.model_json_schema(),
        response=definition.outputs_type.model_json_schema(),
        metadata={
            "x-cache-default": _CACHE_DEFAULT,
            "x-require-approval": _REQUIRE_APPROVAL,
        },
        handler=_handler,
    )


def list_workflow_tools(
    *,
    service_factory: Callable[[], client.ExaService] | None = None,
) -> Iterable[WorkflowFunctionTool]:
    """Yield workflow function tools for every registered workflow."""
    for definition in registry.list():
        yield workflow_function_tool(
            definition.name,
            service_factory=service_factory,
        )
