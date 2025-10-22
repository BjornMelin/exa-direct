"""Built-in workflows registered for CLI, Responses, and Agents reuse."""

from __future__ import annotations

from typing import Any, Literal

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

    instructions: str = Field(
        ...,
        description="Natural-language research request.",
        examples=["Summarize the latest retrieval-augmented generation research"],
        json_schema_extra={"x-redact": True},
    )
    model: (
        Literal[
            "exa-research-fast",
            "exa-research",
            "exa-research-pro",
        ]
        | None
    ) = Field(
        default="exa-research-fast",
        description="Research model to use.",
    )
    output_schema: dict[str, Any] | None = Field(
        default=None,
        description="Optional JSON Schema dict for structured output.",
        examples=[{"type": "object", "properties": {"summary": {"type": "string"}}}],
        json_schema_extra={"x-redact": True},
    )
    wait_for_completion: bool = Field(
        default=True,
        description="Poll the research task until completion.",
    )


class ResearchRunOutputs(WorkflowOutputs):
    """Outputs for the ``research_run`` workflow."""

    task: dict[str, Any] = Field(
        ...,
        description="Research task payload returned by Exa.",
        json_schema_extra={"x-redact": True},
    )


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
    context.log_step("research.start", status="start")
    created = steps.start_research(
        service,
        instructions=inputs.instructions,
        model=inputs.model,
        schema=inputs.output_schema,
    )
    context.log_step("research.start", status="success")
    if not inputs.wait_for_completion:
        return ResearchRunOutputs(task=created)
    research_id = created.get("id")
    if research_id is None:
        raise ValueError("Research task creation response missing 'id'")
    context.log_step("research.poll", status="start")
    final = steps.poll_research(service, research_id=research_id)
    context.log_step("research.poll", status="success")
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

    query: str = Field(
        ...,
        description="Context query text.",
        examples=["FastAPI async dependency injection"],
    )
    tokens_num: str | int | None = Field(
        default="dynamic",
        description="Token budget (integer or 'dynamic').",
        examples=["dynamic", 5000],
    )


class ContextBuildOutputs(WorkflowOutputs):
    """Outputs for the ``context_build`` workflow."""

    context: dict[str, Any] = Field(
        ...,
        description="Context payload returned by Exa context endpoint.",
        json_schema_extra={"x-redact": True},
    )


def _plan_context(inputs: ContextBuildInputs) -> list[ExecutionPlanStep]:
    return [
        ExecutionPlanStep(
            name="context.query", description="Fetch code-aware context for the query."
        )
    ]


def _run_context(inputs: ContextBuildInputs, context) -> ContextBuildOutputs:
    """Execute the context-build workflow."""
    context.log_step("context.query", status="start")
    result = steps.query_context(
        context.service, query=inputs.query, tokens_num=inputs.tokens_num
    )
    context.log_step("context.query", status="success")
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

    query: str = Field(
        ...,
        description="Search query.",
        examples=["retrieval augmented generation benchmarks"],
    )
    type_: Literal["auto", "neural", "keyword", "fast", "hybrid", "deep"] | None = (
        Field(
            default=None,
            alias="type",
            description="Search type.",
        )
    )
    num_results: int | None = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of results to return.",
    )
    fetch_contents: bool = Field(
        default=False,
        description="Fetch contents for each result via search_and_contents.",
    )


class SearchCollectOutputs(WorkflowOutputs):
    """Outputs for the ``search_collect`` workflow."""

    results: dict[str, Any] = Field(
        ...,
        description="Combined search (and optionally contents) results.",
        json_schema_extra={"x-redact": True},
    )


def _plan_search(inputs: SearchCollectInputs) -> list[ExecutionPlanStep]:
    description = (
        "Search and fetch inline contents." if inputs.fetch_contents else "Search"
    )
    return [ExecutionPlanStep(name="search", description=description)]


def _run_search(inputs: SearchCollectInputs, context) -> SearchCollectOutputs:
    """Execute the search-collect workflow."""
    context.log_step("search", status="start")
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
    context.log_step("search", status="success")
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

    query: str = Field(
        ...,
        description="Search query forwarded from CLI arguments.",
    )
    search_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Search parameters constructed from CLI flags.",
    )
    contents_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Contents parameters constructed from CLI flags.",
    )


class SearchCLIOutputs(WorkflowOutputs):
    """Outputs for the single-step CLI search workflow."""

    results: dict[str, Any] = Field(
        ...,
        description="Search or search_and_contents payload.",
        json_schema_extra={"x-redact": True},
    )


def _run_search_cli(inputs: SearchCLIInputs, context) -> SearchCLIOutputs:
    """Execute the compatibility search workflow."""
    context.log_step("search_cli", status="start")
    results = steps.run_search(
        context.service,
        query=inputs.query,
        search_params=inputs.search_params,
        contents_params=inputs.contents_params or None,
    )
    context.log_step("search_cli", status="success")
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

    urls: list[str] = Field(
        ...,
        description="List of URLs to fetch.",
        min_length=1,
    )
    options: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional contents options (livecrawl, summaries, etc.).",
    )


class ContentsCLIOutputs(WorkflowOutputs):
    """Outputs for the single-step CLI contents workflow."""

    contents: dict[str, Any] = Field(
        ...,
        description="Contents response payload from Exa.",
        json_schema_extra={"x-redact": True},
    )


def _run_contents_cli(inputs: ContentsCLIInputs, context) -> ContentsCLIOutputs:
    """Execute the compatibility contents workflow."""
    context.log_step("contents_cli", status="start")
    result = context.service.contents(urls=inputs.urls, **inputs.options)
    context.log_step("contents_cli", status="success")
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

    url: str = Field(..., description="Seed URL for similarity search.")
    find_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Similarity search parameters constructed from CLI flags.",
    )
    contents_params: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional contents parameters when fetching result pages.",
    )


class FindSimilarCLIOutputs(WorkflowOutputs):
    """Outputs for the single-step CLI similarity workflow."""

    results: dict[str, Any] = Field(
        ...,
        description="Similarity (and optionally contents) payload from Exa.",
        json_schema_extra={"x-redact": True},
    )


def _run_find_similar_cli(
    inputs: FindSimilarCLIInputs, context
) -> FindSimilarCLIOutputs:
    """Execute the compatibility find-similar workflow."""
    context.log_step("find_similar_cli", status="start")
    result = steps.run_find_similar(
        context.service,
        url=inputs.url,
        find_params=inputs.find_params or None,
        contents_params=inputs.contents_params or None,
    )
    context.log_step("find_similar_cli", status="success")
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

    query: str = Field(..., description="Natural-language question for Exa Answer.")
    options: dict[str, Any] = Field(
        default_factory=dict,
        description="Answer options (model, include_text, streaming flags).",
        json_schema_extra={"x-redact": True},
    )


class AnswerCLIOutputs(WorkflowOutputs):
    """Outputs for the single-step CLI answer workflow."""

    answer: dict[str, Any] = Field(
        ...,
        description="Answer payload returned by Exa.",
        json_schema_extra={"x-redact": True},
    )


def _run_answer_cli(inputs: AnswerCLIInputs, context) -> AnswerCLIOutputs:
    """Execute the compatibility answer workflow."""
    context.log_step("answer_cli", status="start")
    result = context.service.answer(query=inputs.query, **inputs.options)
    context.log_step("answer_cli", status="success")
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
