from diagramm.generators.mermaid import to_mermaid
from diagramm.generators.plantuml import to_plantuml
from diagramm.model import Diagram, Edge, Node


def _sample_diagram() -> Diagram:
    nodes = (
        Node(id="start", type="start"),
        Node(id="step", type="action", label="Шаг"),
        Node(id="decision", type="decision", label="Условие?"),
        Node(id="end", type="end"),
    )
    edges = (
        Edge(from_id="start", to_id="step"),
        Edge(from_id="step", to_id="decision"),
        Edge(from_id="decision", to_id="end", condition="да"),
    )
    return Diagram(diagram_type="activity", nodes=nodes, edges=edges)


def test_mermaid_output_contains_edges():
    diagram = _sample_diagram()
    output = to_mermaid(diagram)
    assert "start" in output
    assert "decision" in output
    assert "-->" in output
    assert "|да|" in output


def test_plantuml_output_contains_transitions():
    diagram = _sample_diagram()
    output = to_plantuml(diagram)
    assert "@startuml" in output
    assert "[*] --> start" in output
    assert "start --> step" in output
    assert "decision --> end : да" in output
    assert "end --> [*]" in output
