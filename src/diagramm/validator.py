from __future__ import annotations

from collections import Counter

from jsonschema import Draft202012Validator

from diagramm.model import (
    ALLOWED_DIAGRAM_TYPES,
    ALLOWED_NODE_TYPES,
    START_END_REQUIRED,
    Diagram,
    ValidationResult,
)
from diagramm.schema import LLM_SCHEMA


class DiagramValidator:
    def __init__(self) -> None:
        self._schema_validator = Draft202012Validator(LLM_SCHEMA)

    def validate_payload(self, payload: dict) -> ValidationResult:
        errors: list[str] = []
        for error in sorted(self._schema_validator.iter_errors(payload), key=str):
            errors.append(f"schema: {error.message}")

        if errors:
            return ValidationResult.fail(errors)

        return self.validate_diagram(Diagram.from_payload(payload))

    def validate_diagram(self, diagram: Diagram) -> ValidationResult:
        errors: list[str] = []

        if diagram.diagram_type not in ALLOWED_DIAGRAM_TYPES:
            errors.append(f"diagram_type '{diagram.diagram_type}' is not supported")

        node_ids = [node.id for node in diagram.nodes]
        if len(node_ids) != len(set(node_ids)):
            duplicates = [node_id for node_id, count in Counter(node_ids).items() if count > 1]
            errors.append(f"duplicate node ids: {', '.join(sorted(duplicates))}")

        for node in diagram.nodes:
            if node.type not in ALLOWED_NODE_TYPES:
                errors.append(f"node '{node.id}' has unsupported type '{node.type}'")

        node_id_set = set(node_ids)
        for edge in diagram.edges:
            if edge.from_id not in node_id_set:
                errors.append(f"edge from '{edge.from_id}' references missing node")
            if edge.to_id not in node_id_set:
                errors.append(f"edge to '{edge.to_id}' references missing node")

        if diagram.diagram_type in START_END_REQUIRED:
            types = {node.type for node in diagram.nodes}
            if "start" not in types:
                errors.append("diagram requires a start node")
            if "end" not in types:
                errors.append("diagram requires an end node")

        outgoing = Counter(edge.from_id for edge in diagram.edges)
        incoming = Counter(edge.to_id for edge in diagram.edges)

        for node in diagram.nodes:
            if diagram.diagram_type in START_END_REQUIRED:
                if node.type == "start" and outgoing[node.id] == 0:
                    errors.append("start node must have at least one outgoing edge")
                if node.type == "end" and incoming[node.id] == 0:
                    errors.append("end node must have at least one incoming edge")

            if incoming[node.id] == 0 and outgoing[node.id] == 0:
                errors.append(f"node '{node.id}' is isolated")

        if errors:
            return ValidationResult.fail(errors)
        return ValidationResult.ok()
