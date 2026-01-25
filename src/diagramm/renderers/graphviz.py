from __future__ import annotations

from pathlib import Path

from diagramm.renderers.base import RenderError, ensure_parent_dir, require_command, run_command


def render_to_png(input_path: Path, output_path: Path, **_opts: object) -> None:
    if not input_path.exists():
        raise RenderError(f"Input file does not exist: {input_path}")
    require_command("dot", "Install Graphviz and ensure `dot` is available on PATH.")
    ensure_parent_dir(output_path)
    command = ["dot", "-Tpng", str(input_path), "-o", str(output_path)]
    run_command(command, "Graphviz failed to render PNG")
