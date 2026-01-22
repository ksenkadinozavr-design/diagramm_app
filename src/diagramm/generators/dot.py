from __future__ import annotations

from diagramm.model import Diagram, Edge

PORTS = {
    "input": "w",
    "control": "n",
    "output": "e",
    "mechanism": "s",
}


def _format_label(label: str) -> str:
    return label.replace("\"", "\\\"")


def _edge_with_ports(edge: Edge) -> tuple[str, str, str | None]:
    if not edge.condition:
        return edge.from_id, edge.to_id, None

    condition = edge.condition.strip().lower()
    port = PORTS.get(condition)
    if not port:
        return edge.from_id, edge.to_id, edge.condition

    if condition == "output":
        return f"{edge.from_id}:{port}", edge.to_id, None
    return edge.from_id, f"{edge.to_id}:{port}", None


def _style_lines(style: str | None) -> list[str]:
    if style != "idef0":
        return ["  rankdir=LR;", "  node [shape=box];"]

    return [
        "  graph [rankdir=LR, splines=ortho, nodesep=0.6, ranksep=1.0, bgcolor=\"#fafafa\", fontname=\"Arial\", fontsize=10];",
        "  node [shape=box, style=\"rounded,filled\", fillcolor=\"#ffffff\", color=\"#4a4a4a\", penwidth=1, fontname=\"Arial\", fontsize=10, margin=\"0.12,0.08\"];",
        "  edge [color=\"#4a4a4a\", arrowsize=0.7, fontname=\"Arial\", fontsize=9];",
    ]


def to_dot(diagram: Diagram, *, style: str | None = None) -> str:
    lines = ["digraph diagramm {", *_style_lines(style)]

    for node in diagram.nodes:
        label = _format_label(node.label or node.id)
        lines.append(f'  {node.id} [label="{label}"];')

    for edge in diagram.edges:
        from_id, to_id, label = _edge_with_ports(edge)
        if label:
            lines.append(f'  {from_id} -> {to_id} [label="{_format_label(label)}"];')
        else:
            lines.append(f"  {from_id} -> {to_id};")

    lines.append("}")
    return "\n".join(lines)
