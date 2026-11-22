"""Tests for named scenarios, automatic versions and model comparison."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "web"))

from api import registry, workspaces  # noqa: E402
from api.main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_workspaces():
    original = registry.WEB_ROOT
    with tempfile.TemporaryDirectory() as directory:
        registry.WEB_ROOT = Path(directory)
        workspaces.registry.WEB_ROOT = Path(directory)
        yield
        registry.WEB_ROOT = original
        workspaces.registry.WEB_ROOT = original


def _scenario(client: TestClient, name: str):
    response = client.post(
        "/api/atlas/scenarios", json={"name": name, "description": "Experiment"}
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_scenarios_snapshots_and_compare():
    initial = client.get("/api/atlas/scenarios").json()
    assert initial["active"] == "base"
    assert [item["name"] for item in initial["scenarios"]] == ["base"]

    payload = _scenario(client, "variant-a")
    assert payload["active"] == "variant-a"
    entry = next(item for item in payload["scenarios"] if item["name"] == "variant-a")
    assert entry["description"] == "Experiment"
    assert [version["version"] for version in entry["versions"]] == [1]

    # The live model switches to the new scenario and can be edited independently.
    model = client.get("/api/atlas/model").json()["files"]
    changed = model["components.yaml"].replace("criticality: P0", "criticality: P9")
    assert "criticality: P9" in changed
    assert client.put(
        "/api/atlas/model/components.yaml", json={"content": changed}
    ).status_code == 200

    saved = client.post("/api/atlas/snapshots", json={"label": "raised criticality"}).json()
    entry = next(item for item in saved["scenarios"] if item["name"] == "variant-a")
    assert [version["version"] for version in entry["versions"]] == [1, 2]
    assert entry["versions"][1]["label"] == "raised criticality"

    comparison = client.get(
        "/api/atlas/compare?left=variant-a:1&right=variant-a:2"
    ).json()
    assert comparison["left"] == "variant-a/v001"
    assert comparison["right"] == "variant-a/v002"
    component_diff = next(item for item in comparison["files"] if item["file"] == "components.yaml")
    assert component_diff["changed"] is True
    assert "-  criticality: P0" in component_diff["diff"] or any(
        "criticality" in line and "- " in line for line in component_diff["diff"].splitlines()
    )

    # Switching back restores the base model.
    client.post("/api/atlas/scenarios/base/activate")
    assert client.get("/api/atlas/scenarios").json()["active"] == "base"
    assert "criticality: P9" not in client.get("/api/atlas/model").json()["files"]["components.yaml"]

    client.post("/api/atlas/scenarios/variant-a/activate")
    assert "criticality: P9" in client.get("/api/atlas/model").json()["files"]["components.yaml"]

    deleted = client.delete("/api/atlas/scenarios/variant-a").json()
    assert deleted["active"] == "base"
    assert [item["name"] for item in deleted["scenarios"]] == ["base"]


def test_scenario_validation():
    assert client.post("/api/atlas/scenarios", json={"name": "../bad"}).status_code == 400
    assert client.post("/api/atlas/scenarios", json={"name": "base"}).status_code == 400
    assert client.delete("/api/atlas/scenarios/base").status_code == 400
    assert (
        client.get("/api/atlas/compare?left=base&right=missing").status_code == 400
    )
