from __future__ import annotations

import json

from diagramm.model import Diagram


def to_json(diagram: Diagram) -> str:
    payload = {
        "diagram_type": diagram.diagram_type,
        "nodes": [
            {"id": node.id, "type": node.type, "label": node.label}
            for node in diagram.nodes
        ],
        "edges": [
            {
                "from": edge.from_id,
                "to": edge.to_id,
                **({"condition": edge.condition} if edge.condition else {}),
            }
            for edge in diagram.edges
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
