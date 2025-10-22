"""Workflow base classes and execution helpers."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Generic, Protocol, TypeVar, cast
from uuid import uuid4

from pydantic import BaseModel, ConfigDict
from structlog.stdlib import BoundLogger

from ..structured_logging import bind, get_logger, redact_payload


class WorkflowInputs(BaseModel):
    """Marker base type for workflow inputs."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class WorkflowOutputs(BaseModel):
    """Marker base type for workflow outputs."""

    model_config = ConfigDict(extra="forbid")


InputsT_contra = TypeVar("InputsT_contra", bound=WorkflowInputs, contravariant=True)
OutputsT_co = TypeVar("OutputsT_co", bound=WorkflowOutputs, covariant=True)


class Planner(Protocol[InputsT_contra]):
    """Protocol describing a callable that generates execution plans."""

    def __call__(self, inputs: InputsT_contra) -> Sequence[ExecutionPlanStep]:
        """Return the steps that would be executed for the provided inputs."""
        raise NotImplementedError


class Runner(Protocol[InputsT_contra, OutputsT_co]):
    """Protocol describing a callable that executes a workflow."""

    def __call__(self, inputs: InputsT_contra, context: WorkflowContext) -> OutputsT_co:
        """Execute the workflow and return validated outputs."""
        raise NotImplementedError


@dataclass
class ExecutionPlanStep:
    """Describes a single planned step."""

    name: str
    description: str


@dataclass
class WorkflowContext:
    """Execution context available to workflow runners."""

    workflow_id: str
    service: Any
    logger_name: str = "exa_direct.workflow"

    @property
    def logger(self) -> BoundLogger:
        """Structlog logger bound to the workflow context."""
        return cast(BoundLogger, get_logger(self.logger_name))

    def log_step(self, step: str, *, status: str = "start", **metadata: Any) -> None:
        """Emit a workflow.step event for the current workflow."""
        self.logger.info("workflow.step", step=step, status=status, **metadata)

    def log_retry(self, step: str, *, attempt: int, **metadata: Any) -> None:
        """Emit a workflow.retry event for the current workflow."""
        self.logger.info("workflow.retry", step=step, attempt=attempt, **metadata)


@dataclass
class WorkflowDefinition(Generic[InputsT_contra, OutputsT_co]):  # noqa: UP046
    """Metadata and execution hooks for a workflow."""

    name: str
    summary: str
    inputs_type: type[InputsT_contra]
    outputs_type: type[OutputsT_co]
    run: Runner[InputsT_contra, OutputsT_co]
    planner: Planner[InputsT_contra] | None = None

    def plan(self, inputs: InputsT_contra) -> list[ExecutionPlanStep]:
        """Return the planned execution steps for ``inputs``."""
        if self.planner is None:
            return []
        return list(self.planner(inputs))


def execute(
    definition: WorkflowDefinition[InputsT_contra, OutputsT_co],
    service: Any,
    inputs: InputsT_contra,
) -> OutputsT_co:
    """Execute the workflow and emit structured logging events."""
    workflow_id = str(uuid4())
    with bind(workflow_id=workflow_id):
        logger = cast(
            BoundLogger,
            get_logger("exa_direct.workflow").bind(workflow=definition.name),
        )
        inputs_payload = redact_payload(inputs.model_dump(exclude_none=True))
        logger.info("workflow.start", inputs=inputs_payload)
        plan = definition.plan(inputs)
        if plan:
            logger.info(
                "workflow.plan",
                steps=[
                    {"name": step.name, "description": step.description}
                    for step in plan
                ],
            )
        context = WorkflowContext(workflow_id=workflow_id, service=service)
        result = definition.run(inputs, context)
        outputs_payload = redact_payload(result.model_dump(exclude_none=True))
        logger.info("workflow.succeeded", outputs=outputs_payload)
    return result
