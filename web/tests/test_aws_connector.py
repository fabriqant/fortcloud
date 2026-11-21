"""Tests for the optional read-only AWS inventory connector."""

from __future__ import annotations

import yaml

from connectors.aws import build_document


class FakePaginator:
    def __init__(self, pages: list[dict]):
        self.pages = pages

    def paginate(self, **kwargs):
        return self.pages


class FakeClient:
    def __init__(self, pages: dict[str, list[dict]]):
        self.pages = pages

    def get_paginator(self, method: str) -> FakePaginator:
        return FakePaginator(self.pages[method])


class FakeSession:
    def __init__(self, clients: dict[str, FakeClient]):
        self.clients = clients

    def client(self, service: str, region_name: str | None = None):
        return self.clients[service]


def _session() -> FakeSession:
    return FakeSession(
        {
            "ec2": FakeClient(
                {
                    "describe_instances": [
                        {
                            "Reservations": [
                                {
                                    "Instances": [
                                        {
                                            "InstanceId": "i-1",
                                            "Tags": [
                                                {"Key": "Name", "Value": "api"},
                                                {"Key": "owner", "Value": "platform"},
                                            ],
                                            "Placement": {"AvailabilityZone": "eu-west-3a"},
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ),
            "rds": FakeClient(
                {
                    "describe_db_instances": [
                        {
                            "DBInstances": [
                                {
                                    "DBInstanceIdentifier": "primary",
                                    "MultiAZ": True,
                                    "AvailabilityZone": "eu-west-3a",
                                    "TagList": [{"Key": "Owner", "Value": "data"}],
                                }
                            ]
                        }
                    ]
                }
            ),
            "s3": FakeClient({"list_buckets": [{"Buckets": [{"Name": "data"}]}]}),
        }
    )


def test_build_document_maps_aws_resources():
    document = build_document(_session(), "eu-west-3")

    assert document["version"] == 1
    identifiers = [component["id"] for component in document["components"]]
    assert identifiers == ["ec2-api-i-1", "rds-primary", "s3-data"]
    assert len(identifiers) == len(set(identifiers))

    ec2, rds, s3 = document["components"]
    assert ec2["name"] == "EC2 api"
    assert ec2["owner"] == "platform"
    assert ec2["zones"] == ["eu-west-3a"]
    assert rds["redundancy"]["instances"] == 2
    assert rds["redundancy"]["replication"] == "sync"
    assert s3["category"] == "storage"

    for component in document["components"]:
        assert component["provider"] == "aws"
        assert component["regions"] == ["eu-west-3"]
        assert component["criticality"] == "P1"
        assert "redundancy" in component


def test_document_round_trips_as_yaml():
    document = build_document(_session(), "eu-west-3")
    content = yaml.safe_dump(document, sort_keys=False, allow_unicode=True)
    assert yaml.safe_load(content) == document
