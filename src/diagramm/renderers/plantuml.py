from __future__ import annotations

import os
import shutil
from pathlib import Path

from diagramm.renderers.base import RenderError, ensure_parent_dir, require_command, run_command


def _resolve_command(plantuml_jar: str | None) -> list[str]:
    plantuml_path = shutil.which("plantuml")
    if plantuml_path:
        return [plantuml_path]

    jar_path = plantuml_jar or os.environ.get("PLANTUML_JAR")
    if not jar_path:
        raise RenderError(
            "PlantUML is not available. Install `plantuml` or set PLANTUML_JAR."
        )
    if not Path(jar_path).exists():
        raise RenderError(f"PLANTUML_JAR not found at: {jar_path}")

    require_command("java", "Install Java to use PlantUML JAR.")
    return ["java", "-jar", jar_path]


def render_to_png(
    input_path: Path, output_path: Path, *, plantuml_jar: str | None = None, **_opts: object
) -> None:
    if not input_path.exists():
        raise RenderError(f"Input file does not exist: {input_path}")
    ensure_parent_dir(output_path)
    command = _resolve_command(plantuml_jar)
    command += ["-tpng", str(input_path)]
    run_command(command, "PlantUML failed to render PNG")

    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    expected_path = input_path.with_suffix(".png")
    fallback_path = output_dir / f"{input_path.stem}.png"

    if expected_path.exists():
        source_path = expected_path
    elif fallback_path.exists():
        source_path = fallback_path
    else:
        raise RenderError(
            f"PlantUML output not found: {expected_path} or {fallback_path}"
        )

    if source_path.resolve() != output_path.resolve():
        output_path.unlink(missing_ok=True)
        source_path.replace(output_path)
