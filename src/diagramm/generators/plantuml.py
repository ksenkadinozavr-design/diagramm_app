from __future__ import annotations

from diagramm.model import Diagram


def _format_label(label: str) -> str:
    return label.replace("\"", "\\\"")


def to_plantuml(diagram: Diagram) -> str:
    lines = ["@startuml", "hide empty description"]

    for node in diagram.nodes:
        if node.type in {"start", "end"} and not node.label:
            continue
        label = _format_label(node.label or node.id)
        lines.append(f'state "{label}" as {node.id}')

    start_nodes = [node for node in diagram.nodes if node.type == "start"]
    end_nodes = {node.id for node in diagram.nodes if node.type == "end"}

    if start_nodes:
        for node in start_nodes:
            lines.append(f"[*] --> {node.id}")
    else:
        if diagram.nodes:
            lines.append(f"[*] --> {diagram.nodes[0].id}")

    for edge in diagram.edges:
        condition = f" : {edge.condition}" if edge.condition else ""
        lines.append(f"{edge.from_id} --> {edge.to_id}{condition}")

    for end_id in end_nodes:
        lines.append(f"{end_id} --> [*]")

    lines.append("@enduml")
    return "\n".join(lines)
