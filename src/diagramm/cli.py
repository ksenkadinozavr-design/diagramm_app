from __future__ import annotations

import argparse
import contextlib
import json
import sys
import tempfile
from pathlib import Path

from diagramm.generators.json_export import to_json
from diagramm.generators.mermaid import to_mermaid
from diagramm.generators.plantuml import to_plantuml
from diagramm.generators.dot import to_dot
from diagramm.classifier import classify_text
from diagramm.model import Diagram
from diagramm.normalizer import normalize
from diagramm.renderers import graphviz, mermaid, plantuml
from diagramm.renderers.base import RenderError
from diagramm.schema import LLM_SCHEMA
from diagramm.validator import DiagramValidator


def _load_payload(path: str) -> dict | None:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        return None


def _write_output(content: str, output: str | None) -> None:
    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        print(content)


def _load_diagram(path: str) -> Diagram | None:
    payload = _load_payload(path)
    if payload is None:
        return None
    validator = DiagramValidator()
    result = validator.validate_payload(payload)
    if not result.valid:
        for error in result.errors:
            print(f"ERROR: {error}")
        return None
    return normalize(Diagram.from_payload(payload))


def _renderer_format_from_engine(engine: str) -> str:
    return {
        "graphviz": "dot",
        "plantuml": "plantuml",
        "mermaid": "mermaid",
    }[engine]


def _default_engine(diagram_type: str) -> str | None:
    return {
        "idef0": "graphviz",
        "idef1x": "plantuml",
        "idef3": "plantuml",
        "idef4": "plantuml",
        "idef5": "graphviz",
    }.get(diagram_type)


def _ensure_png_output(output: str | None) -> Path | None:
    if not output:
        print("ERROR: --output is required for PNG rendering.")
        return None
    return Path(output)


@contextlib.contextmanager
def _intermediate_dir(tmpdir: str | None, keep: bool):
    if tmpdir:
        path = Path(tmpdir)
        path.mkdir(parents=True, exist_ok=True)
        yield path
        return
    if keep:
        path = Path(tempfile.mkdtemp(prefix="diagramm-"))
        yield path
        return
    with tempfile.TemporaryDirectory(prefix="diagramm-") as temp_dir:
        yield Path(temp_dir)


def command_validate(path: str) -> int:
    payload = _load_payload(path)
    if payload is None:
        return 1
    validator = DiagramValidator()
    result = validator.validate_payload(payload)
    if result.valid:
        print("OK")
        return 0

    for error in result.errors:
        print(f"ERROR: {error}")
    return 1


def command_generate(
    path: str, format_name: str, output: str | None, render: str | None
) -> int:
    diagram = _load_diagram(path)
    if diagram is None:
        return 1

    generators = {
        "mermaid": to_mermaid,
        "plantuml": to_plantuml,
        "json": to_json,
        "dot": to_dot,
    }
    generator = generators.get(format_name)
    if not generator:
        print(f"Unsupported format: {format_name}")
        return 1

    output_path = Path(output) if output else None
    render_png = render == "png" or (output_path and output_path.suffix == ".png")
    if render_png:
        if format_name == "json":
            print("ERROR: JSON format cannot be rendered to PNG.")
            return 1
        if output_path is None:
            print("ERROR: --output is required for PNG rendering.")
            return 1
        content = generator(diagram)
        with _intermediate_dir(None, False) as temp_dir:
            extension = {
                "mermaid": ".mmd",
                "plantuml": ".puml",
                "dot": ".dot",
            }[format_name]
            intermediate_path = temp_dir / f"diagram{extension}"
            intermediate_path.write_text(content, encoding="utf-8")
            engine = {
                "mermaid": "mermaid",
                "plantuml": "plantuml",
                "dot": "graphviz",
            }[format_name]
            renderer = {
                "graphviz": graphviz.render_to_png,
                "plantuml": plantuml.render_to_png,
                "mermaid": mermaid.render_to_png,
            }[engine]
            try:
                renderer(intermediate_path, output_path)
            except RenderError as exc:
                print(f"ERROR: {exc}")
                return 1
        return 0

    _write_output(generator(diagram), output)
    return 0


def command_normalize(path: str, output: str | None) -> int:
    payload = _load_payload(path)
    if payload is None:
        return 1
    diagram = normalize(Diagram.from_payload(payload))
    _write_output(to_json(diagram), output)
    return 0


def command_schema(output: str | None) -> int:
    _write_output(json.dumps(LLM_SCHEMA, ensure_ascii=False, indent=2), output)
    return 0


def command_classify(path: str | None) -> int:
    if path:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    else:
        lines = sys.stdin.read().splitlines()
    diagram_type = classify_text(lines)
    print(diagram_type)
    return 0


def command_render(
    path: str,
    output: str | None,
    engine: str | None,
    keep_intermediate: bool,
    tmpdir: str | None,
) -> int:
    diagram = _load_diagram(path)
    if diagram is None:
        return 1

    selected_engine = engine or _default_engine(diagram.diagram_type)
    if not selected_engine:
        print(
            "ERROR: Unable to infer renderer; specify --engine explicitly for this diagram type."
        )
        return 1

    output_path = _ensure_png_output(output)
    if output_path is None:
        return 1

    format_name = _renderer_format_from_engine(selected_engine)
    generator = {
        "mermaid": to_mermaid,
        "plantuml": to_plantuml,
        "dot": to_dot,
    }[format_name]
    renderer = {
        "graphviz": graphviz.render_to_png,
        "plantuml": plantuml.render_to_png,
        "mermaid": mermaid.render_to_png,
    }[selected_engine]

    with _intermediate_dir(tmpdir, keep_intermediate) as temp_dir:
        extension = {
            "mermaid": ".mmd",
            "plantuml": ".puml",
            "dot": ".dot",
        }[format_name]
        intermediate_path = temp_dir / f"diagram{extension}"
        intermediate_path.write_text(generator(diagram), encoding="utf-8")
        try:
            renderer(intermediate_path, output_path)
        except RenderError as exc:
            print(f"ERROR: {exc}")
            return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Diagramm CLI for validation and rendering"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate diagram JSON")
    validate.add_argument("path", help="path to JSON file")

    generate = subparsers.add_parser("generate", help="generate diagram output")
    generate.add_argument("path", help="path to JSON file")
    generate.add_argument(
        "--format",
        required=True,
        choices=["mermaid", "plantuml", "json", "dot"],
        help="output format",
    )
    generate.add_argument("--output", help="optional output file path")
    generate.add_argument(
        "--render",
        choices=["png"],
        help="render output (e.g. png) using external renderer",
    )

    render = subparsers.add_parser("render", help="render diagram to PNG")
    render.add_argument("path", help="path to JSON file")
    render.add_argument("--output", required=True, help="output PNG file path")
    render.add_argument(
        "--engine",
        choices=["graphviz", "plantuml", "mermaid"],
        help="renderer engine (default depends on diagram type)",
    )
    render.add_argument(
        "--keep-intermediate",
        action="store_true",
        help="keep intermediate .dot/.puml/.mmd files",
    )
    render.add_argument(
        "--tmpdir", help="temporary directory for intermediate files"
    )

    normalize_cmd = subparsers.add_parser(
        "normalize", help="normalize diagram JSON payload"
    )
    normalize_cmd.add_argument("path", help="path to JSON file")
    normalize_cmd.add_argument("--output", help="optional output file path")

    schema_cmd = subparsers.add_parser("schema", help="print JSON schema")
    schema_cmd.add_argument("--output", help="optional output file path")

    classify_cmd = subparsers.add_parser(
        "classify", help="classify text into a diagram type"
    )
    classify_cmd.add_argument(
        "--path", help="optional text file path; if omitted, reads stdin"
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "validate":
        sys.exit(command_validate(args.path))
    if args.command == "generate":
        sys.exit(command_generate(args.path, args.format, args.output, args.render))
    if args.command == "normalize":
        sys.exit(command_normalize(args.path, args.output))
    if args.command == "schema":
        sys.exit(command_schema(args.output))
    if args.command == "classify":
        sys.exit(command_classify(args.path))
    if args.command == "render":
        sys.exit(
            command_render(
                args.path,
                args.output,
                args.engine,
                args.keep_intermediate,
                args.tmpdir,
            )
        )


if __name__ == "__main__":
    main()
