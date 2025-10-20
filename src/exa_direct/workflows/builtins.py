"""Built-in workflows registered for CLI, Responses, and Agents reuse."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from . import steps
from .base import (
    ExecutionPlanStep,
    WorkflowDefinition,
    WorkflowInputs,
    WorkflowOutputs,
)
from .registry import registry


class ResearchRunInputs(WorkflowInputs):
    """Inputs for the ``research_run`` workflow."""

    instructions: str = Field(..., description="Natural-language research request.")
    model: str | None = Field(
        default="exa-research-fast",
        description=(
            "Research model to use (exa-research-fast, exa-research, exa-research-pro)."
        ),
    )
    output_schema: dict[str, Any] | None = Field(
        default=None, description="Optional JSON Schema dict for structured output."
    )
    wait_for_completion: bool = Field(
        default=True, description="Poll the research task until completion."
    )


class ResearchRunOutputs(WorkflowOutputs):
    """Outputs for the ``research_run`` workflow."""

    task: dict[str, Any]


def _plan_research(inputs: ResearchRunInputs) -> list[ExecutionPlanStep]:
    plan: list[ExecutionPlanStep] = [
        ExecutionPlanStep(
            name="research.start",
            description="Submit research task to Exa research endpoint.",
        )
    ]
    if inputs.wait_for_completion:
        plan.append(
            ExecutionPlanStep(
                name="research.poll", description="Poll research task until completion."
            )
        )
    return plan


def _run_research(inputs: ResearchRunInputs, context) -> ResearchRunOutputs:
    """Execute the research workflow using the provided inputs."""
    service = context.service
    created = steps.start_research(
        service,
        instructions=inputs.instructions,
        model=inputs.model,
        schema=inputs.output_schema,
    )
    if not inputs.wait_for_completion:
        return ResearchRunOutputs(task=created)
    research_id = created.get("id")
    if research_id is None:
        raise ValueError("Research task creation response missing 'id'")
    final = steps.poll_research(service, research_id=research_id)
    return ResearchRunOutputs(task=final)


registry.register(
    WorkflowDefinition(
        name="research_run",
        summary=("Start an Exa research task and optionally wait for completion."),
        inputs_type=ResearchRunInputs,
        outputs_type=ResearchRunOutputs,
        run=_run_research,
        planner=_plan_research,
    )
)


class ContextBuildInputs(WorkflowInputs):
    """Inputs for the ``context_build`` workflow."""

    query: str = Field(..., description="Context query text.")
    tokens_num: str | int | None = Field(
        default="dynamic", description="Token budget (integer or 'dynamic')."
    )


class ContextBuildOutputs(WorkflowOutputs):
    """Outputs for the ``context_build`` workflow."""

    context: dict[str, Any]


def _plan_context(inputs: ContextBuildInputs) -> list[ExecutionPlanStep]:
    return [
        ExecutionPlanStep(
            name="context.query", description="Fetch code-aware context for the query."
        )
    ]


def _run_context(inputs: ContextBuildInputs, context) -> ContextBuildOutputs:
    """Execute the context-build workflow."""
    result = steps.query_context(
        context.service, query=inputs.query, tokens_num=inputs.tokens_num
    )
    return ContextBuildOutputs(context=result)


registry.register(
    WorkflowDefinition(
        name="context_build",
        summary=(
            "Fetch context results suitable for retrieval-augmented generation "
            "and code workflows."
        ),
        inputs_type=ContextBuildInputs,
        outputs_type=ContextBuildOutputs,
        run=_run_context,
        planner=_plan_context,
    )
)


class SearchCollectInputs(WorkflowInputs):
    """Inputs for the ``search_collect`` workflow."""

    query: str = Field(..., description="Search query.")
    type_: str | None = Field(
        default=None,
        alias="type",
        description="Search type (auto, neural, keyword, fast, hybrid, deep).",
    )
    num_results: int | None = Field(
        default=10, description="Number of results to return."
    )
    fetch_contents: bool = Field(
        default=False,
        description="Fetch contents for each result via search_and_contents.",
    )


class SearchCollectOutputs(WorkflowOutputs):
    """Outputs for the ``search_collect`` workflow."""

    results: dict[str, Any]


def _plan_search(inputs: SearchCollectInputs) -> list[ExecutionPlanStep]:
    description = (
        "Search and fetch inline contents." if inputs.fetch_contents else "Search"
    )
    return [ExecutionPlanStep(name="search", description=description)]


def _run_search(inputs: SearchCollectInputs, context) -> SearchCollectOutputs:
    """Execute the search-collect workflow."""
    search_params: dict[str, Any] = {}
    if inputs.type_:
        search_params["type"] = inputs.type_
    if inputs.num_results is not None:
        search_params["num_results"] = inputs.num_results
    contents_params: dict[str, Any] | None = (
        {"text": True} if inputs.fetch_contents else None
    )
    results = steps.run_search(
        context.service,
        query=inputs.query,
        search_params=search_params,
        contents_params=contents_params,
    )
    return SearchCollectOutputs(results=results)


registry.register(
    WorkflowDefinition(
        name="search_collect",
        summary=("Perform a search and optionally retrieve result contents inline."),
        inputs_type=SearchCollectInputs,
        outputs_type=SearchCollectOutputs,
        run=_run_search,
        planner=_plan_search,
    )
)


# ---------------------------------------------------------------------------
# CLI compatibility workflows (single-step wrappers)


class SearchCLIInputs(WorkflowInputs):
    """Inputs for the single-step CLI search workflow."""

    query: str
    search_params: dict[str, Any] = Field(default_factory=dict)
    contents_params: dict[str, Any] = Field(default_factory=dict)


class SearchCLIOutputs(WorkflowOutputs):
    """Outputs for the single-step CLI search workflow."""

    results: dict[str, Any]


def _run_search_cli(inputs: SearchCLIInputs, context) -> SearchCLIOutputs:
    """Execute the compatibility search workflow."""
    results = steps.run_search(
        context.service,
        query=inputs.query,
        search_params=inputs.search_params,
        contents_params=inputs.contents_params or None,
    )
    return SearchCLIOutputs(results=results)


registry.register(
    WorkflowDefinition(
        name="search_cli",
        summary="Legacy CLI search mapping (single-step).",
        inputs_type=SearchCLIInputs,
        outputs_type=SearchCLIOutputs,
        run=_run_search_cli,
    )
)


class ContentsCLIInputs(WorkflowInputs):
    """Inputs for the single-step CLI contents workflow."""

    urls: list[str]
    options: dict[str, Any] = Field(default_factory=dict)


class ContentsCLIOutputs(WorkflowOutputs):
    """Outputs for the single-step CLI contents workflow."""

    contents: dict[str, Any]


def _run_contents_cli(inputs: ContentsCLIInputs, context) -> ContentsCLIOutputs:
    """Execute the compatibility contents workflow."""
    result = context.service.contents(urls=inputs.urls, **inputs.options)
    return ContentsCLIOutputs(contents=result)


registry.register(
    WorkflowDefinition(
        name="contents_cli",
        summary="Legacy CLI contents mapping (single-step).",
        inputs_type=ContentsCLIInputs,
        outputs_type=ContentsCLIOutputs,
        run=_run_contents_cli,
    )
)


class FindSimilarCLIInputs(WorkflowInputs):
    """Inputs for the single-step CLI similarity workflow."""

    url: str
    find_params: dict[str, Any] = Field(default_factory=dict)
    contents_params: dict[str, Any] = Field(default_factory=dict)


class FindSimilarCLIOutputs(WorkflowOutputs):
    """Outputs for the single-step CLI similarity workflow."""

    results: dict[str, Any]


def _run_find_similar_cli(
    inputs: FindSimilarCLIInputs, context
) -> FindSimilarCLIOutputs:
    """Execute the compatibility find-similar workflow."""
    result = steps.run_find_similar(
        context.service,
        url=inputs.url,
        find_params=inputs.find_params or None,
        contents_params=inputs.contents_params or None,
    )
    return FindSimilarCLIOutputs(results=result)


registry.register(
    WorkflowDefinition(
        name="find_similar_cli",
        summary="Legacy CLI find-similar mapping (single-step).",
        inputs_type=FindSimilarCLIInputs,
        outputs_type=FindSimilarCLIOutputs,
        run=_run_find_similar_cli,
    )
)


class AnswerCLIInputs(WorkflowInputs):
    """Inputs for the single-step CLI answer workflow."""

    query: str
    options: dict[str, Any] = Field(default_factory=dict)


class AnswerCLIOutputs(WorkflowOutputs):
    """Outputs for the single-step CLI answer workflow."""

    answer: dict[str, Any]


def _run_answer_cli(inputs: AnswerCLIInputs, context) -> AnswerCLIOutputs:
    """Execute the compatibility answer workflow."""
    result = context.service.answer(query=inputs.query, **inputs.options)
    return AnswerCLIOutputs(answer=result)


registry.register(
    WorkflowDefinition(
        name="answer_cli",
        summary="Legacy CLI answer mapping (single-step).",
        inputs_type=AnswerCLIInputs,
        outputs_type=AnswerCLIOutputs,
        run=_run_answer_cli,
    )
)
