from __future__ import annotations

import shutil
from pathlib import Path

from diagramm.renderers.base import RenderError, ensure_parent_dir, require_command, run_command


def render_to_png(input_path: Path, output_path: Path, **_opts: object) -> None:
    if not input_path.exists():
        raise RenderError(f"Input file does not exist: {input_path}")

    command = None
    if shutil.which("mmdc"):
        command = ["mmdc", "-i", str(input_path), "-o", str(output_path)]
    elif shutil.which("npx"):
        command = ["npx", "@mermaid-js/mermaid-cli", "-i", str(input_path), "-o", str(output_path)]
    else:
        raise RenderError(
            "Mermaid CLI is not available. Install `mmdc` or ensure `npx` is on PATH."
        )

    ensure_parent_dir(output_path)
    run_command(command, "Mermaid failed to render PNG")
