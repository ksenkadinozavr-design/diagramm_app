from __future__ import annotations

from diagramm.model import Diagram

NODE_SHAPES = {
    "start": "([",
    "end": "([",
    "decision": "{",
    "action": "[",
    "process": "[",
    "input": "[/",
    "output": "[/",
    "entity": "[",
    "store": "[(",
    "actor": "((",
    "class": "[",
}

NODE_SHAPES_END = {
    "start": "])",
    "end": "])",
    "decision": "}",
    "action": "]",
    "process": "]",
    "input": "/]",
    "output": "/]",
    "entity": "]",
    "store": ")]",
    "actor": "))",
    "class": "]",
}


def to_mermaid(diagram: Diagram) -> str:
    lines = ["flowchart TD"]
    for node in diagram.nodes:
        label = node.label or node.id
        start = NODE_SHAPES.get(node.type, "[")
        end = NODE_SHAPES_END.get(node.type, "]")
        lines.append(f"    {node.id}{start}{label}{end}")

    for edge in diagram.edges:
        if edge.condition:
            lines.append(f"    {edge.from_id} -->|{edge.condition}| {edge.to_id}")
        else:
            lines.append(f"    {edge.from_id} --> {edge.to_id}")
    return "\n".join(lines)
