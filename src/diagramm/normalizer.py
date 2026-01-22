from __future__ import annotations

from diagramm.model import Diagram, Edge, Node


def normalize(diagram: Diagram) -> Diagram:
    normalized_nodes = []
    for node in diagram.nodes:
        label = node.label.strip() if node.label else None
        node_id = node.id.strip()
        node_type = node.type.strip().lower()
        normalized_nodes.append(Node(id=node_id, type=node_type, label=label or None))

    normalized_edges = []
    for edge in diagram.edges:
        condition = edge.condition.strip() if edge.condition else None
        normalized_edges.append(
            Edge(
                from_id=edge.from_id.strip(),
                to_id=edge.to_id.strip(),
                condition=condition or None,
            )
        )

    return Diagram(
        diagram_type=diagram.diagram_type.strip().lower(),
        nodes=tuple(normalized_nodes),
        edges=tuple(normalized_edges),
    )
