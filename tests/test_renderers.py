from pathlib import Path

import pytest

from diagramm.renderers import graphviz, mermaid, plantuml
from diagramm.renderers.base import RenderError


def test_graphviz_renderer_builds_command(monkeypatch, tmp_path):
    commands = []

    def fake_run(command, _message):
        commands.append(command)

    monkeypatch.setattr(graphviz, "require_command", lambda *_args, **_kwargs: "/usr/bin/dot")
    monkeypatch.setattr(graphviz, "run_command", fake_run)

    input_path = tmp_path / "diagram.dot"
    input_path.write_text("digraph {}", encoding="utf-8")
    output_path = tmp_path / "out.png"

    graphviz.render_to_png(input_path, output_path)

    assert commands == [["dot", "-Tpng", str(input_path), "-o", str(output_path)]]


def test_plantuml_renderer_uses_expected_output(monkeypatch, tmp_path):
    commands = []

    def fake_run(command, _message):
        commands.append(command)
        (tmp_path / "diagram.png").write_text("png", encoding="utf-8")

    monkeypatch.setattr(plantuml, "_resolve_command", lambda *_args, **_kwargs: ["plantuml"])
    monkeypatch.setattr(plantuml, "run_command", fake_run)

    input_path = tmp_path / "diagram.puml"
    input_path.write_text("@startuml", encoding="utf-8")
    output_path = tmp_path / "custom.png"

    plantuml.render_to_png(input_path, output_path)

    assert commands
    assert output_path.exists()


def test_mermaid_renderer_prefers_mmdc(monkeypatch, tmp_path):
    commands = []

    def fake_run(command, _message):
        commands.append(command)

    monkeypatch.setattr(mermaid.shutil, "which", lambda name: "/usr/bin/mmdc" if name == "mmdc" else None)
    monkeypatch.setattr(mermaid, "run_command", fake_run)

    input_path = tmp_path / "diagram.mmd"
    input_path.write_text("flowchart TD", encoding="utf-8")
    output_path = tmp_path / "out.png"

    mermaid.render_to_png(input_path, output_path)

    assert commands == [["mmdc", "-i", str(input_path), "-o", str(output_path)]]


def test_mermaid_renderer_errors_without_cli(monkeypatch, tmp_path):
    monkeypatch.setattr(mermaid.shutil, "which", lambda _name: None)

    input_path = tmp_path / "diagram.mmd"
    input_path.write_text("flowchart TD", encoding="utf-8")
    output_path = tmp_path / "out.png"

    with pytest.raises(RenderError):
        mermaid.render_to_png(input_path, output_path)
