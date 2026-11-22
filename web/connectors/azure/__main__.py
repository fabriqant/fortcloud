"""Command line entry point: python -m connectors.azure --help"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml

from .collector import DEFAULT_IMPORT_FILE, build_document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Propose an Atlas component inventory from read-only Azure APIs."
    )
    parser.add_argument(
        "--subscription-id",
        default=os.environ.get("AZURE_SUBSCRIPTION_ID"),
        help="Azure subscription ID (default: AZURE_SUBSCRIPTION_ID)",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_IMPORT_FILE),
        help="Path of the proposed components.yaml",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the YAML without writing it")
    args = parser.parse_args(argv)

    if not args.subscription_id:
        print("An Azure subscription ID is required.", file=sys.stderr)
        return 2

    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.resource import ResourceManagementClient
    except ImportError:
        print(
            "Azure SDKs are required. Install them with:\n"
            "  python -m pip install -r web/connectors/requirements-azure.txt",
            file=sys.stderr,
        )
        return 2

    credential = DefaultAzureCredential()
    client = ResourceManagementClient(credential, args.subscription_id)
    document = build_document(client, args.subscription_id)
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
