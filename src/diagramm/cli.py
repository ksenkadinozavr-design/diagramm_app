from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from diagramm.generators.json_export import to_json
from diagramm.generators.mermaid import to_mermaid
from diagramm.generators.plantuml import to_plantuml
from diagramm.classifier import classify_text
from diagramm.model import Diagram
from diagramm.normalizer import normalize
from diagramm.schema import LLM_SCHEMA
from diagramm.validator import DiagramValidator


def _load_payload(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_output(content: str, output: str | None) -> None:
    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        print(content)


def command_validate(path: str) -> int:
    payload = _load_payload(path)
    validator = DiagramValidator()
    result = validator.validate_payload(payload)
    if result.valid:
        print("OK")
        return 0

    for error in result.errors:
        print(f"ERROR: {error}")
    return 1


def command_generate(path: str, format_name: str, output: str | None) -> int:
    payload = _load_payload(path)
    validator = DiagramValidator()
    result = validator.validate_payload(payload)
    if not result.valid:
        for error in result.errors:
            print(f"ERROR: {error}")
        return 1

    diagram = normalize(Diagram.from_payload(payload))
    if format_name == "mermaid":
        _write_output(to_mermaid(diagram), output)
        return 0
    if format_name == "plantuml":
        _write_output(to_plantuml(diagram), output)
        return 0
    if format_name == "json":
        _write_output(to_json(diagram), output)
        return 0

    print(f"Unsupported format: {format_name}")
    return 1


def command_normalize(path: str, output: str | None) -> int:
    payload = _load_payload(path)
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
        choices=["mermaid", "plantuml", "json"],
        help="output format",
    )
    generate.add_argument("--output", help="optional output file path")

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
        sys.exit(command_generate(args.path, args.format, args.output))
    if args.command == "normalize":
        sys.exit(command_normalize(args.path, args.output))
    if args.command == "schema":
        sys.exit(command_schema(args.output))
    if args.command == "classify":
        sys.exit(command_classify(args.path))


if __name__ == "__main__":
    main()
