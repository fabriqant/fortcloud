"""Tests for the optional read-only Azure inventory connector."""

from __future__ import annotations

import yaml

from connectors.azure import build_document


class FakeResources:
    def __init__(self, resources: list[dict]):
        self.resources = resources

    def list(self):
        return self.resources


class FakeResourceClient:
    def __init__(self, resources: list[dict]):
        self.resources = FakeResources(resources)


def test_build_document_maps_azure_resources():
    client = FakeResourceClient(
        [
            {
                "id": "/subscriptions/s/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/api",
                "name": "api",
                "type": "Microsoft.Compute/virtualMachines",
                "location": "francecentral",
                "zones": ["1", "2"],
                "tags": {"owner": "platform", "environment": "prod"},
            },
            {
                "id": "/subscriptions/s/providers/Microsoft.Sql/servers/db-server/databases/core",
                "name": "core",
                "type": "Microsoft.Sql/servers/databases",
                "location": "westeurope",
                "tags": {"Owner": "data"},
            },
            {
                "id": "/subscriptions/s/providers/Microsoft.Storage/storageAccounts/data",
                "name": "data",
                "type": "Microsoft.Storage/storageAccounts",
                "location": "francecentral",
                "tags": {},
            },
            {"name": "ignored", "type": "Microsoft.Network/virtualNetworks"},
        ]
    )

    document = build_document(client, "subscription-id")

    assert document["version"] == 1
    assert len(document["components"]) == 3
    vm, database, storage = document["components"]
    assert vm["id"].startswith("azure-microsoft-compute-virtualmachines")
    assert vm["name"] == "Azure VM api"
    assert vm["category"] == "processing"
    assert vm["owner"] == "platform"
    assert vm["environments"] == ["prod"]
    assert vm["regions"] == ["francecentral"]
    assert vm["zones"] == ["1", "2"]
    assert database["category"] == "storage"
    assert database["owner"] == "data"
    assert storage["category"] == "storage"

    for component in document["components"]:
        assert component["provider"] == "azure"
        assert component["criticality"] == "P1"
        assert component["backup"]["enabled"] is False


def test_document_round_trips_as_yaml():
    client = FakeResourceClient(
        [
            {
                "name": "api",
                "type": "Microsoft.Compute/virtualMachines",
                "location": "francecentral",
            }
        ]
    )
    document = build_document(client)
    assert yaml.safe_load(yaml.safe_dump(document, sort_keys=False)) == document
