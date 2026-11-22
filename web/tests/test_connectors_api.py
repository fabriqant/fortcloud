"""Tests for the local connector registry and runner."""

from __future__ import annotations

import subprocess

import pytest
from fastapi.testclient import TestClient

from api import connectors
from api.connectors import ConnectorError, ConnectorRun
from api.main import app

client = TestClient(app)


def _fake_run(calls: list) -> object:
    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, stdout="Wrote 2 components\n", stderr="")

    return run


def test_describe_lists_all_providers_without_secrets():
    providers = connectors.describe()
    assert [provider["id"] for provider in providers] == ["aws", "azure", "gcp"]
    assert all(provider["fields"] for provider in providers)
    assert all(provider["proposal"] == "components.yaml" for provider in providers)


def test_run_invokes_allowlisted_local_connector(monkeypatch: pytest.MonkeyPatch):
    calls: list = []
    monkeypatch.setattr(connectors.subprocess, "run", _fake_run(calls))

    result = connectors.run(ConnectorRun(provider="aws", profile="prod", region="eu-west-3"))

    assert result["ok"] is True
    assert result["proposal"] == "components.yaml"
    assert "connectors.aws" in result["command"]
    assert "--profile prod" in result["command"]
    assert "--region eu-west-3" in result["command"]
    assert calls[0][1]["cwd"] == connectors.WEB_ROOT
    assert calls[0][1]["capture_output"] is True


def test_run_rejects_unknown_provider_and_unsafe_values():
    with pytest.raises(ConnectorError, match="Unknown connector"):
        connectors.run(ConnectorRun(provider="nope"))
    with pytest.raises(ConnectorError, match="Invalid value"):
        connectors.run(ConnectorRun(provider="aws", region="eu-west-3; rm -rf /"))


def test_connector_api_endpoints(monkeypatch: pytest.MonkeyPatch):
    calls: list = []
    monkeypatch.setattr(connectors.subprocess, "run", _fake_run(calls))

    listing = client.get("/api/connectors")
    assert listing.status_code == 200
    assert len(listing.json()) == 3

    result = client.post("/api/connectors/run", json={"provider": "gcp", "project_id": "my-project"})
    assert result.status_code == 200
    assert result.json()["provider"] == "gcp"
    assert "--project-id my-project" in result.json()["command"]

    rejected = client.post("/api/connectors/run", json={"provider": "nope"})
    assert rejected.status_code == 400
