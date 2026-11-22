"""Command line entry point: python -m connectors.gcp --help"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml

from .collector import DEFAULT_IMPORT_FILE, build_document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Propose an Atlas component inventory from read-only Google Cloud APIs."
    )
    parser.add_argument(
        "--project-id",
        default=os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCLOUD_PROJECT"),
        help="Google Cloud project ID (default: GOOGLE_CLOUD_PROJECT)",
    )
    parser.add_argument(
        "--out",
        default=str(DEFAULT_IMPORT_FILE),
        help="Path of the proposed components.yaml",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the YAML without writing it")
    args = parser.parse_args(argv)

    if not args.project_id:
        print("A Google Cloud project ID is required.", file=sys.stderr)
        return 2

    try:
        import google.auth
        from google.cloud import compute_v1, storage
        from googleapiclient.discovery import build
    except ImportError:
        print(
            "Google Cloud SDKs are required. Install them with:\n"
            "  python -m pip install -r web/connectors/requirements-gcp.txt",
            file=sys.stderr,
        )
        return 2

    warnings: list[str] = []

    try:
        instances = list(
            compute_v1.InstancesClient().list_instances(project=args.project_id, zone="all-zones")
        )
    except Exception as exc:  # an API may be disabled for this project
        warnings.append(f"Compute Engine skipped: {str(exc)[:200]}")
        instances = []

    try:
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        sql_service = build("sqladmin", "v1beta4", credentials=credentials, cache_discovery=False)
        sql_instances = sql_service.instances().list(project=args.project_id).execute().get("items", [])
    except Exception as exc:
        warnings.append(f"Cloud SQL skipped: {str(exc)[:200]}")
        sql_instances = []

    try:
        buckets = list(storage.Client(project=args.project_id).list_buckets())
    except Exception as exc:
        warnings.append(f"Cloud Storage skipped: {str(exc)[:200]}")
        buckets = []

    document = build_document(args.project_id, instances, sql_instances, buckets)
    content = yaml.safe_dump(document, sort_keys=False, allow_unicode=True)

    for warning in warnings:
        print(f"Warning: {warning}", file=sys.stderr)

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
