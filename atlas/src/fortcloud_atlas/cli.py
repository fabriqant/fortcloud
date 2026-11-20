"""Command-line interface for Fortcloud Atlas."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, core, render, validate


def _configure_output() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


def _add_model_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--model",
        default=str(core.DEFAULT_MODEL),
        help="directory with the four YAML files (default: hybrid/multi-cloud example)",
    )
    parser.add_argument(
        "--schema-dir",
        default=None,
        help="directory with the JSON Schemas (default: auto-detection)",
    )


def _add_output_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--out",
        default=str(core.DEFAULT_OUTPUT),
        help="output directory for generated artifacts",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fortcloud-atlas",
        description="Fortcloud Atlas — Dependency & Risk Map for hybrid and multi-cloud infrastructure.",
    )
    parser.add_argument("--version", action="version", version=f"fortcloud-atlas {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    validate_parser = commands.add_parser("validate", help="validate the YAML model")
    _add_model_arguments(validate_parser)
    validate_parser.add_argument(
        "--strict", action="store_true", help="treat warnings as errors"
    )

    graph_parser = commands.add_parser("graph", help="generate the Mermaid dependency graph")
    _add_model_arguments(graph_parser)
    _add_output_argument(graph_parser)

    report_parser = commands.add_parser("report", help="generate the resilience report")
    _add_model_arguments(report_parser)
    _add_output_argument(report_parser)

    check_parser = commands.add_parser(
        "check", help="validate, then generate the graph and the report"
    )
    _add_model_arguments(check_parser)
    _add_output_argument(check_parser)
    check_parser.add_argument(
        "--strict", action="store_true", help="treat warnings as errors"
    )

    return parser


def _display(label: str, items: list[str]) -> None:
    if not items:
        return
    print(f"\n{label} ({len(items)})")
    for item in items:
        print(f"  - {item}")


def _diagnose(args, strict: bool = False) -> tuple[dict | None, bool]:
    model, errors, warnings = validate.collect(args.model, args.schema_dir)
    print("Fortcloud Atlas — model validation")
    _display("ERRORS", errors)
    _display("WARNINGS", warnings)
    if errors:
        return None, False
    if strict and warnings:
        print("\nFAILED: warnings are errors in strict mode.")
        return model, False
    if model:
        print(
            f"\nOK: {len(model['components'])} components, "
            f"{len(model['dependencies'])} dependencies, "
            f"{len(model['flows'])} flows, {len(model['risks'])} risks."
        )
    return model, True


def _show_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    _configure_output()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        _, ok = _diagnose(args, strict=args.strict)
        return 0 if ok else 1

    model, ok = _diagnose(args, strict=getattr(args, "strict", False))
    if not ok or model is None:
        return 1

    if args.command == "graph":
        path = render.write_graph(model, args.out)
        print(f"Graph written: {_show_path(path)}")
        return 0

    if args.command == "report":
        path = render.write_report(model, args.out)
        print(f"Report written: {_show_path(path)}")
        return 0

    if args.command == "check":
        graph_path = render.write_graph(model, args.out)
        report_path = render.write_report(model, args.out)
        print(f"Graph written: {_show_path(graph_path)}")
        print(f"Report written: {_show_path(report_path)}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
