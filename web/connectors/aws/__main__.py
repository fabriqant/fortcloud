"""Command line entry point: python -m connectors.aws --help"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from .collector import DEFAULT_IMPORT_FILE, build_document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Propose an Atlas component inventory from read-only AWS APIs."
    )
    parser.add_argument("--profile", help="AWS profile name from the local AWS configuration")
    parser.add_argument("--region", default="eu-west-3", help="AWS region to inspect")
    parser.add_argument(
        "--out",
        default=str(DEFAULT_IMPORT_FILE),
        help="Path of the proposed components.yaml",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the YAML without writing it")
    args = parser.parse_args(argv)

    try:
        import boto3
    except ImportError:
        print(
            "boto3 is required. Install it with:\n"
            "  python -m pip install -r web/connectors/requirements-aws.txt",
            file=sys.stderr,
        )
        return 2

    session = (
        boto3.Session(profile_name=args.profile, region_name=args.region)
        if args.profile
        else boto3.Session(region_name=args.region)
    )
    document = build_document(session, args.region)
    content = yaml.safe_dump(document, sort_keys=False, allow_unicode=True)

    if args.dry_run:
        print(content, end="")
        return 0

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"Wrote {len(document['components'])} components to {output}")
    print("Review the proposal in the console Import tab before accepting it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
