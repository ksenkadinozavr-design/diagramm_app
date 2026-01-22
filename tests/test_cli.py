import json

from diagramm import cli


def _write_payload(path, diagram_type="idef0"):
    payload = {
        "diagram_type": diagram_type,
        "nodes": [
            {"id": "Input", "type": "input"},
            {"id": "A1", "type": "process"},
        ],
        "edges": [{"from": "Input", "to": "A1", "condition": "input"}],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_render_command_uses_default_engine(monkeypatch, tmp_path):
    input_path = tmp_path / "diagram.json"
    _write_payload(input_path)
    output_path = tmp_path / "out.png"

    def fake_render(_input, output):
        output.write_text("png", encoding="utf-8")

    monkeypatch.setattr(cli.graphviz, "render_to_png", fake_render)

    result = cli.command_render(
        str(input_path),
        str(output_path),
        engine=None,
        keep_intermediate=False,
        tmpdir=None,
    )

    assert result == 0
    assert output_path.exists()


def test_generate_command_renders_png(monkeypatch, tmp_path):
    input_path = tmp_path / "diagram.json"
    _write_payload(input_path)
    output_path = tmp_path / "out.png"

    def fake_render(_input, output):
        output.write_text("png", encoding="utf-8")

    monkeypatch.setattr(cli.graphviz, "render_to_png", fake_render)

    result = cli.command_generate(
        str(input_path),
        format_name="dot",
        output=str(output_path),
        render="png",
    )

    assert result == 0
    assert output_path.exists()
