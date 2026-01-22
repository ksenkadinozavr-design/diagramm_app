from diagramm.generators.dot import to_dot
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


def test_dot_output_contains_ports_for_roles():
    diagram = Diagram(
        diagram_type="idef0",
        nodes=(
            Node(id="A1", type="process", label="Auth"),
            Node(id="Input", type="input"),
            Node(id="Output", type="output"),
        ),
        edges=(
            Edge(from_id="Input", to_id="A1", condition="input"),
            Edge(from_id="A1", to_id="Output", condition="output"),
        ),
    )
    output = to_dot(diagram)
    assert "Input -> A1:w" in output
    assert "A1:e -> Output" in output
