"""OpenAI Agents SDK integration helpers.

This module exposes utilities to compose workflow-backed specialist agents and a
lightweight coordinator descriptor for orchestration with the OpenAI Agents
SDK. It complements the Responses function-tool helpers by providing
Agent-friendly wrappers that intentionally keep the underlying service alive for
multi-step agent runs (no per-call close).

Key entry points:

- ``workflow_tool(name)`` - wrap a registered workflow as an Agents SDK
  ``function_tool`` (async callable).
- ``CoordinatorSettings`` - minimal settings for the coordinator agent.
- ``list_workflow_specialists()`` - yield one specialist (``agents.Agent``)
  per registered workflow.
- ``build_coordinator(settings)`` - return a coordinator descriptor and the
  full set of specialists.
"""

# pylint: disable=duplicate-code

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from agents import Agent, Runner, function_tool

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
    """Return an Agents SDK ``function_tool`` for a workflow.

    The returned callable is async and intentionally does not close the
    underlying service instance. Agents often perform multiple tool calls within
    a single run; the service lifecycle is delegated to the orchestrator.
    """
    definition = registry.get(name)
    factory = service_factory or _default_service_factory

    @function_tool(
        name_override=f"workflow_{definition.name}",
        description_override=definition.summary,
        strict_mode=False,
    )
    async def _tool(**kwargs: Any) -> dict[str, Any]:
        inputs = definition.inputs_type(**kwargs)
        service = factory()

        def _run_sync() -> dict[str, Any]:
            result = registry.execute(name, service, inputs)
            return result.model_dump(exclude_none=True)

        # Run the synchronous workflow execution off the event loop.
        return await asyncio.to_thread(_run_sync)

    return _tool


# ----------------------------- Coordinator API ----------------------------- #


@dataclass(slots=True)
class CoordinatorSettings:
    """Minimal configuration for the coordinator agent.

    Attributes:
        model: Model name to use for coordinator reasoning (e.g., ``"gpt-4.1-mini"``).
        instructions: Optional system instructions. If omitted, a default playbook
            is generated that documents coordinator responsibilities.
    """

    model: str
    instructions: str | None = None
    max_turns: int | None = None
    specialist_model: str | None = None


@dataclass(slots=True)
class SpecialistDescriptor:
    """Describes a workflow-backed specialist agent."""

    name: str
    description: str
    tool_name: str
    agent: Any


@dataclass(slots=True)
class CoordinatorDescriptor:
    """Lightweight descriptor for the coordinator agent."""

    name: str
    instructions: str
    agent: Any | None


def list_workflow_specialists(
    *, service_factory: Callable[[], client.ExaService] | None = None
) -> Iterable[SpecialistDescriptor]:
    """Yield a specialist per registered workflow.

    Each specialist is a simple ``agents.Agent`` with a single tool—the wrapped
    workflow callable produced by :func:`workflow_tool`.
    """
    specialist_model_env = os.getenv("EXA_DIRECT_AGENTS_SPECIALIST_MODEL")
    for definition in registry.list():
        tool = workflow_tool(definition.name, service_factory=service_factory)
        agent = Agent(
            name=definition.name,
            instructions=(
                f"You are the specialist for the '{definition.name}' workflow. "
                "Execute the provided tool precisely using validated inputs."
            ),
            tools=[tool],
            model=specialist_model_env or None,
        )
        yield SpecialistDescriptor(
            name=definition.name,
            description=definition.summary,
            tool_name=f"workflow_{definition.name}",
            agent=agent,
        )


def _default_coordinator_instructions(
    specialists: Iterable[SpecialistDescriptor],
) -> str:
    names = ", ".join(spec.name for spec in specialists)
    lines: list[str] = []
    lines.extend([
        ("Responsibilities: Coordinate planning and route calls."),
        ("Ensure inputs/outputs match each tool's Pydantic schema."),
        ("Iterate: if information is incomplete, refine and call tools again."),
        ("Validate key facts across multiple sources."),
        (
            "Routing: quick Q&A → answer_cli; synthesis/tables → research_run; "
            "fresh data → search_cli then contents_cli;"
        ),
        ("neighbors → find_similar_cli;"),
        ("code → exa_context."),
        ("For contents_cli: pass URLs from prior search."),
        ("Prefer highlights first; fetch full text only when needed."),
        f"Available specialists: {names}",
    ])
    return "\n\n".join(lines)


def _direct_exa_tools(
    service_factory: Callable[[], client.ExaService] | None,
):
    """Return a list of low-level Exa function tools for flexible chaining."""
    factory = service_factory or _default_service_factory

    @function_tool(
        name_override="exa_search",
        description_override="Call Exa search. Args: query:str, params:object.",
        strict_mode=False,
    )
    async def _exa_search(*, query: str, params: dict[str, Any] | None = None):
        svc = factory()
        return await asyncio.to_thread(
            lambda: svc.search(query=query, params=params or {})
        )

    @function_tool(
        name_override="exa_contents",
        description_override="Call Exa contents. Args: urls:list[str], options:object.",
        strict_mode=False,
    )
    async def _exa_contents(*, urls: list[str], options: dict[str, Any] | None = None):
        svc = factory()
        return await asyncio.to_thread(
            lambda: svc.contents(urls=urls, **(options or {}))
        )

    @function_tool(
        name_override="exa_answer",
        description_override="Call Exa answer. Args: query:str, options:object.",
        strict_mode=False,
    )
    async def _exa_answer(*, query: str, options: dict[str, Any] | None = None):
        svc = factory()
        opts = options or {}
        return await asyncio.to_thread(lambda: svc.answer(query=query, **opts))

    @function_tool(
        name_override="exa_find_similar",
        description_override="Call Exa find_similar. Args: url:str, params:object.",
        strict_mode=False,
    )
    async def _exa_find_similar(*, url: str, params: dict[str, Any] | None = None):
        svc = factory()
        return await asyncio.to_thread(
            lambda: svc.find_similar(url=url, params=params or {})
        )

    @function_tool(
        name_override="exa_search_and_contents",
        description_override=(
            "Call Exa search_and_contents. Args: query:str; search_params:object; "
            "content_params:object."
        ),
        strict_mode=False,
    )
    async def _exa_search_and_contents(
        *,
        query: str,
        search_params: dict[str, Any] | None = None,
        content_params: dict[str, Any] | None = None,
    ):
        svc = factory()
        return await asyncio.to_thread(
            lambda: svc.search_and_contents(
                query=query,
                search_params=search_params or {},
                content_params=content_params or {},
            )
        )

    @function_tool(
        name_override="exa_find_similar_and_contents",
        description_override=(
            "Call Exa find_similar_and_contents. Args: url:str; find_params:object; "
            "content_params:object."
        ),
        strict_mode=False,
    )
    async def _exa_find_similar_and_contents(
        *,
        url: str,
        find_params: dict[str, Any] | None = None,
        content_params: dict[str, Any] | None = None,
    ):
        svc = factory()
        return await asyncio.to_thread(
            lambda: svc.find_similar_and_contents(
                url=url,
                find_params=find_params or {},
                content_params=content_params or {},
            )
        )

    @function_tool(
        name_override="exa_context",
        description_override=(
            "Call Exa Code context. Args: query:str; tokens_num:'dynamic'|int."
        ),
        strict_mode=False,
    )
    async def _exa_context(*, query: str, tokens_num: str | int | None = None):
        svc = factory()
        return await asyncio.to_thread(
            lambda: svc.context(query=query, tokens_num=tokens_num)
        )

    return [
        _exa_search,
        _exa_contents,
        _exa_answer,
        _exa_find_similar,
        _exa_search_and_contents,
        _exa_find_similar_and_contents,
        _exa_context,
    ]


def build_coordinator(
    *,
    settings: CoordinatorSettings,
    service_factory: Callable[[], client.ExaService] | None = None,
) -> tuple[CoordinatorDescriptor, list[SpecialistDescriptor]]:
    """Construct a coordinator agent and the full specialist roster.

    Returns a tuple of ``(coordinator_descriptor, specialists)``. The
    coordinator is a standard ``agents.Agent`` configured with high-level
    instructions; each specialist is an ``agents.Agent`` with exactly one tool.
    """
    # Materialize specialists first so we can reference them in the instructions.
    specialists = list(list_workflow_specialists(service_factory=service_factory))
    instructions = settings.instructions or _default_coordinator_instructions(
        specialists
    )

    # Resolve model selection from settings with env fallbacks
    model = (
        settings.model
        or os.getenv("EXA_DIRECT_AGENTS_COORDINATOR_MODEL")
        or os.getenv("EXA_DIRECT_AGENTS_MODEL")
        or "gpt-4.1-mini"
    )
    specialist_model = (
        settings.specialist_model
        or os.getenv("EXA_DIRECT_AGENTS_SPECIALIST_MODEL")
        or model
    )
    # Ensure specialists carry the chosen specialist model (if missing)
    for spec in specialists:
        if getattr(spec.agent, "model", None) in (None, ""):
            spec.agent = spec.agent.clone(model=specialist_model)

    # Add direct Exa tools for fine-grained chaining
    direct_tools = _direct_exa_tools(service_factory)

    coordinator_agent = Agent(
        name="workflow-orchestrator",
        instructions=instructions,
        tools=[
            # Expose each specialist as a callable tool to the coordinator
            spec.agent.as_tool(
                tool_name=spec.tool_name,
                tool_description=spec.description,
            )
            for spec in specialists
        ]
        + direct_tools,
        model=model,
    )

    return (
        CoordinatorDescriptor(
            name=coordinator_agent.name,
            instructions=instructions,
            agent=coordinator_agent,
        ),
        specialists,
    )


# ------------------------------ Run Orchestration ------------------------------ #


@dataclass(slots=True)
class WorkflowAgentContext:
    """Lightweight context passed to Agents runs.

    Attributes:
        conversation_id: Optional identifier for conversation/session grouping.
    """

    conversation_id: str | None = None


async def run_coordinator(
    prompt: str,
    *,
    settings: CoordinatorSettings | None = None,
    context: WorkflowAgentContext | None = None,
    service_factory: Callable[[], client.ExaService] | None = None,
    session_id: str | None = None,
    session_backend: str | None = None,
    session_db_path: str | None = None,
) -> Any:
    """Run the coordinator agent over the given prompt and return the RunResult.

    This constructs specialists from registered workflows and a coordinating agent
    that has those specialists attached as tools. The OpenAI Agents Runner is used
    for the agent loop and tool execution.
    """
    default_model = (
        os.getenv("EXA_DIRECT_AGENTS_MODEL")
        or os.getenv("EXA_DIRECT_AGENTS_COORDINATOR_MODEL")
        or "gpt-4.1-mini"
    )
    settings = settings or CoordinatorSettings(model=default_model)
    coordinator, _specialists = build_coordinator(
        settings=settings, service_factory=service_factory
    )
    run_kwargs: dict[str, Any] = {}
    if settings.max_turns is not None:
        run_kwargs["max_turns"] = settings.max_turns
    # Optional sessions (SQLite/AdvancedSQLite) if configured
    session_backend = (
        session_backend
        or os.getenv("EXA_DIRECT_AGENTS_SESSION_BACKEND")
        or (
            "sqlite"
            if (session_id or os.getenv("EXA_DIRECT_AGENTS_SESSION_ID"))
            else "none"
        )
    )
    session_obj = None
    resolved_session_id = session_id or os.getenv("EXA_DIRECT_AGENTS_SESSION_ID")
    if session_backend != "none" and resolved_session_id:
        try:
            if session_backend == "advanced_sqlite":
                from agents.extensions.memory import (
                    AdvancedSQLiteSession,  # type: ignore
                )

                session_obj = AdvancedSQLiteSession(
                    session_id=resolved_session_id,
                    db_path=session_db_path
                    or os.getenv("EXA_DIRECT_AGENTS_SESSION_DB", ":memory:"),
                    create_tables=True,
                )
            else:
                from agents.extensions.memory import SQLiteSession  # type: ignore

                session_obj = SQLiteSession(
                    resolved_session_id,
                    db_path=session_db_path
                    or os.getenv("EXA_DIRECT_AGENTS_SESSION_DB", ":memory:"),
                )
        except (
            ImportError,
            ModuleNotFoundError,
            OSError,
            TypeError,
            ValueError,
            RuntimeError,
        ):  # pragma: no cover - optional session import/runtime
            session_obj = None
    # CoordinatorDescriptor.agent is always populated by build_coordinator.
    agent: Agent = coordinator.agent  # type: ignore[assignment]
    return await Runner.run(
        starting_agent=agent,
        input=prompt,
        context=context,  # passes through as RunContextWrapper.context
        session=session_obj,
        **run_kwargs,
    )
