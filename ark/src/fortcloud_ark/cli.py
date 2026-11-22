"""Command-line interface for FortCloud Ark."""

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
        prog="fortcloud-ark",
        description="FortCloud Ark — Restore is a feature, not a hope.",
    )
    parser.add_argument("--version", action="version", version=f"fortcloud-ark {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    validate_parser = commands.add_parser("validate", help="validate the backup/restore model")
    _add_model_arguments(validate_parser)
    validate_parser.add_argument(
        "--strict", action="store_true", help="treat warnings as errors"
    )

    coverage_parser = commands.add_parser("coverage", help="generate the backup coverage matrix")
    _add_model_arguments(coverage_parser)
    _add_output_argument(coverage_parser)

    evidence_parser = commands.add_parser("evidence", help="generate the restore evidence report")
    _add_model_arguments(evidence_parser)
    _add_output_argument(evidence_parser)

    plan_parser = commands.add_parser("plan", help="generate the recovery plan")
    _add_model_arguments(plan_parser)
    _add_output_argument(plan_parser)

    check_parser = commands.add_parser(
        "check", help="validate, then generate all artifacts"
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
    print("FortCloud Ark — model validation")
    _display("ERRORS", errors)
    _display("WARNINGS", warnings)
    if errors:
        return None, False
    if strict and warnings:
        print("\nFAILED: warnings are errors in strict mode.")
        return model, False
    if model:
        print(
            f"\nOK: {len(model['assets'])} assets, "
            f"{len(model['backups'])} backups, "
            f"{len(model['restores'])} restores, "
            f"{len(model['services'])} services."
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

    writers = {
        "coverage": render.write_coverage,
        "evidence": render.write_evidence,
        "plan": render.write_plan,
    }
    if args.command in writers:
        path = writers[args.command](model, args.out)
        print(f"Written: {_show_path(path)}")
        return 0

    if args.command == "check":
        paths = [
            render.write_coverage(model, args.out),
            render.write_evidence(model, args.out),
            render.write_plan(model, args.out),
            render.write_status(model, args.out),
        ]
        for path in paths:
            print(f"Written: {_show_path(path)}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
