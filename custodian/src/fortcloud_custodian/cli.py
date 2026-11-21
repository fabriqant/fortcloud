"""Command-line interface for Fortcloud Custodian."""

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
        prog="fortcloud-custodian",
        description="Fortcloud Custodian — Guard access. Prove every change.",
    )
    parser.add_argument("--version", action="version", version=f"fortcloud-custodian {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    validate_parser = commands.add_parser("validate", help="validate the control model")
    _add_model_arguments(validate_parser)
    validate_parser.add_argument(
        "--strict", action="store_true", help="treat warnings as errors"
    )

    for name, help_text in (
        ("access", "generate the least-privilege access matrix"),
        ("secrets", "generate the secret inventory"),
        ("changes", "generate the change-control report"),
        ("audit", "generate the audit-trail report"),
    ):
        subparser = commands.add_parser(name, help=help_text)
        _add_model_arguments(subparser)
        _add_output_argument(subparser)

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
    print("Fortcloud Custodian — model validation")
    _display("ERRORS", errors)
    _display("WARNINGS", warnings)
    if errors:
        return None, False
    if strict and warnings:
        print("\nFAILED: warnings are errors in strict mode.")
        return model, False
    if model:
        print(
            f"\nOK: {len((model.get('access') or {}).get('environments', []))} environments, "
            f"{len((model.get('access') or {}).get('principals', []))} principals, "
            f"{len((model.get('access') or {}).get('grants', []))} grants, "
            f"{len(model.get('secrets', []))} secrets, "
            f"{len(model.get('changes', []))} pipelines, "
            f"{len((model.get('audit') or {}).get('operations', []))} audited operations."
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
        "access": render.write_access,
        "secrets": render.write_secrets,
        "changes": render.write_changes,
        "audit": render.write_audit,
    }
    if args.command in writers:
        path = writers[args.command](model, args.out)
        print(f"Written: {_show_path(path)}")
        return 0

    if args.command == "check":
        paths = [
            render.write_access(model, args.out),
            render.write_secrets(model, args.out),
            render.write_changes(model, args.out),
            render.write_audit(model, args.out),
            render.write_status(model, args.out),
        ]
        for path in paths:
            print(f"Written: {_show_path(path)}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
