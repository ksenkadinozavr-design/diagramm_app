from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

ALLOWED_DIAGRAM_TYPES = {
    "activity",
    "idef0",
    "idef3",
    "dfd",
    "uml_use_case",
    "uml_activity",
    "uml_class",
    "bpmn",
    "flowchart",
}

ALLOWED_NODE_TYPES = {
    "start",
    "end",
    "action",
    "decision",
    "process",
    "input",
    "output",
    "entity",
    "store",
    "actor",
    "class",
}

START_END_REQUIRED = {
    "activity",
    "uml_activity",
    "bpmn",
    "flowchart",
}


@dataclass(frozen=True)
class Node:
    id: str
    type: str
    label: str | None = None


@dataclass(frozen=True)
class Edge:
    from_id: str
    to_id: str
    condition: str | None = None


@dataclass(frozen=True)
class Diagram:
    diagram_type: str
    nodes: tuple[Node, ...]
    edges: tuple[Edge, ...]

    @classmethod
    def from_payload(cls, payload: dict) -> "Diagram":
        nodes = tuple(Node(**node) for node in payload.get("nodes", []))
        edges = tuple(
            Edge(
                from_id=edge["from"],
                to_id=edge["to"],
                condition=edge.get("condition"),
            )
            for edge in payload.get("edges", [])
        )
        return cls(
            diagram_type=payload.get("diagram_type", ""),
            nodes=nodes,
            edges=edges,
        )


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]

    @classmethod
    def ok(cls) -> "ValidationResult":
        return cls(valid=True, errors=())

    @classmethod
    def fail(cls, errors: Iterable[str]) -> "ValidationResult":
        return cls(valid=False, errors=tuple(errors))
