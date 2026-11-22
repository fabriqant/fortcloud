"""Tests for the optional read-only Google Cloud inventory connector."""

from __future__ import annotations

import yaml

from connectors.gcp import build_document


def test_build_document_maps_gcp_resources():
    document = build_document(
        "my-project",
        instances=[
            {
                "name": "api",
                "zone": "https://www.googleapis.com/compute/v1/projects/my-project/zones/europe-west1-b",
                "labels": {"owner": "platform", "environment": "prod"},
            }
        ],
        sql_instances=[{"name": "core", "region": "europe-west1"}],
        buckets=[{"name": "data", "location": "EU", "labels": {"owner": "data"}}],
    )

    assert document["version"] == 1
    assert [item["id"] for item in document["components"]] == [
        "gcp-compute-my-project-api",
        "gcp-sql-my-project-core",
        "gcp-storage-my-project-data",
    ]
    instance, database, bucket = document["components"]
    assert instance["category"] == "processing"
    assert instance["regions"] == ["europe-west1"]
    assert instance["zones"] == ["europe-west1-b"]
    assert instance["owner"] == "platform"
    assert instance["environments"] == ["prod"]
    assert database["category"] == "storage"
    assert bucket["owner"] == "data"

    for component in document["components"]:
        assert component["provider"] == "gcp"
        assert component["criticality"] == "P1"
        assert component["redundancy"]["instances"] >= 1


def test_document_round_trips_as_yaml():
    document = build_document("my-project", instances=[{"name": "api", "zone": "europe-west1-b"}])
    assert yaml.safe_load(yaml.safe_dump(document, sort_keys=False)) == document
