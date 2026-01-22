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


def _ranked_nodes(diagram: Diagram) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {
        "input": [],
        "control": [],
        "mechanism": [],
        "output": [],
    }
    node_types = {node.id: node.type for node in diagram.nodes}
    for node_id, node_type in node_types.items():
        if node_type in buckets:
            buckets[node_type].append(node_id)
    return buckets


def _style_lines(style: str | None) -> list[str]:
    if style is None:
        return ["  rankdir=LR;", "  node [shape=box];"]

    if style in {"idef", "idef0"}:
        return [
            "  graph [rankdir=LR, splines=ortho, nodesep=0.9, ranksep=1.2, bgcolor=\"#ffffff\", fontname=\"Arial\", fontsize=10, overlap=false, concentrate=false, pad=\"0.2\", ordering=out, pack=true, packmode=graph, newrank=true];",
            "  node [shape=box, style=\"filled\", fillcolor=\"#ffffff\", color=\"#2b2b2b\", penwidth=1, fontname=\"Arial\", fontsize=10, margin=\"0.16,0.10\"];",
            "  edge [color=\"#2b2b2b\", arrowsize=0.7, fontname=\"Arial\", fontsize=9, arrowhead=normal, penwidth=1, minlen=2];",
        ]

    return ["  rankdir=LR;", "  node [shape=box];"]


def to_dot(diagram: Diagram, *, style: str | None = None) -> str:
    lines = ["digraph diagramm {", *_style_lines(style)]

    for node in diagram.nodes:
        label = _format_label(node.label or node.id)
        lines.append(f'  {node.id} [label="{label}"];')

    if style == "idef0":
        buckets = _ranked_nodes(diagram)
        if buckets["control"]:
            lines.append("  { rank=source; " + "; ".join(buckets["control"]) + "; }")
        if buckets["input"]:
            lines.append("  { rank=min; " + "; ".join(buckets["input"]) + "; }")
        if buckets["output"]:
            lines.append("  { rank=max; " + "; ".join(buckets["output"]) + "; }")
        if buckets["mechanism"]:
            lines.append("  { rank=sink; " + "; ".join(buckets["mechanism"]) + "; }")

    for edge in diagram.edges:
        from_id, to_id, label = _edge_with_ports(edge)
        if label:
            lines.append(f'  {from_id} -> {to_id} [label="{_format_label(label)}"];')
        else:
            lines.append(f"  {from_id} -> {to_id};")

    lines.append("}")
    return "\n".join(lines)
