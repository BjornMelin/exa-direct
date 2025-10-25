"""Workflow registry for shared orchestration."""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel

from .base import WorkflowDefinition, execute


class WorkflowRegistry:
    """In-memory registry of available workflows."""

    def __init__(self) -> None:
        """Create an empty workflow registry."""
        self._definitions: dict[str, WorkflowDefinition] = {}

    def register(self, definition: WorkflowDefinition) -> None:
        """Register a new workflow definition."""
        if definition.name in self._definitions:
            raise ValueError(f"Workflow '{definition.name}' already registered")
        self._definitions[definition.name] = definition

    def get(self, name: str) -> WorkflowDefinition:
        """Return the workflow definition for ``name``."""
        try:
            return self._definitions[name]
        except KeyError as exc:
            raise KeyError(f"Unknown workflow '{name}'") from exc

    def list(self) -> Iterable[WorkflowDefinition]:
        """Iterate over registered workflow definitions."""
        return self._definitions.values()

    def inputs_model(self, name: str) -> type[BaseModel]:
        """Return the Pydantic model used for workflow inputs."""
        return self.get(name).inputs_type

    def outputs_model(self, name: str) -> type[BaseModel]:
        """Return the Pydantic model used for workflow outputs."""
        return self.get(name).outputs_type

    def execute(self, name: str, service, inputs: BaseModel):
        """Execute the workflow and return validated outputs."""
        definition = self.get(name)
        return execute(definition, service, inputs)  # type: ignore[arg-type]


registry = WorkflowRegistry()
