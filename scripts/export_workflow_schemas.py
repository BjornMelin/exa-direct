"""Export workflow input/output schemas to docs/schemas."""

from __future__ import annotations

import json
from pathlib import Path

from exa_direct.workflows import registry

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "docs" / "schemas"


def export_schemas() -> None:
    """Write input/output JSON Schemas for every registered workflow."""
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for definition in registry.list():
        input_path = SCHEMA_DIR / f"{definition.name}_input.json"
        output_path = SCHEMA_DIR / f"{definition.name}_output.json"
        input_schema = definition.inputs_type.model_json_schema()
        output_schema = definition.outputs_type.model_json_schema()
        input_path.write_text(
            json.dumps(input_schema, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        output_path.write_text(
            json.dumps(output_schema, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    export_schemas()
