"""Smoke tests for the web API. Run from the repository root with pytest web/tests."""

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
    """Use a temporary workspace root so tests never touch real user models."""
    original = registry.WEB_ROOT
    with tempfile.TemporaryDirectory() as directory:
        registry.WEB_ROOT = Path(directory)
        workspaces.registry.WEB_ROOT = Path(directory)
        yield
        registry.WEB_ROOT = original
        workspaces.registry.WEB_ROOT = original


def test_health_and_registry():
    assert client.get("/api/health").json() == {"status": "ok", "tools": 7}
    tools = client.get("/api/tools").json()
    assert [tool["id"] for tool in tools] == [
        "atlas",
        "failover",
        "ark",
        "ballast",
        "vitals",
        "custodian",
        "crucible",
    ]


def test_model_is_seeded_from_example():
    payload = client.get("/api/atlas/model").json()
    assert sorted(payload["files"]) == [
        "components.yaml",
        "dependencies.yaml",
        "flows.yaml",
        "risks.yaml",
    ]
    assert "components:" in payload["files"]["components.yaml"]


def test_validate_and_check_all_tools():
    for tool in registry.load_tools():
        validated = client.post(f"/api/{tool.id}/validate").json()
        assert validated["exit_code"] == 0, (tool.id, validated["errors"])
        checked = client.post(f"/api/{tool.id}/check").json()
        assert checked["exit_code"] == 0, (tool.id, checked["errors"])
        assert len(checked["artifacts"]) == len(tool.artifacts)
        assert all(artifact["available"] for artifact in checked["artifacts"])


def test_strict_mode_escalates_warnings():
    result = client.post("/api/atlas/validate?strict=true").json()
    assert result["exit_code"] == 1
    assert result["warnings"]


def test_structured_data_and_graph():
    client.post("/api/atlas/check")
    data = client.get("/api/atlas/data").json()
    assert data["summary"]["components"] == 12
    assert data["kpis"][0]["key"] == "spofs"
    assert any(table["id"] == "risks" for table in data["tables"])
    assert data["graph"].startswith("flowchart")


def test_artifact_read_and_model_update():
    client.post("/api/atlas/check")
    artifact = client.get("/api/atlas/artifacts/resilience-report.md").json()
    assert "Resilience Report" in artifact["content"]

    filename = "components.yaml"
    original = client.get("/api/atlas/model").json()["files"][filename]
    response = client.put(
        f"/api/atlas/model/{filename}", json={"content": original.replace("P0", "P1")}
    )
    assert response.status_code == 200
    assert "P1" in client.get("/api/atlas/model").json()["files"][filename]

    assert client.put("/api/atlas/model/unknown.yaml", json={"content": "x"}).status_code == 404
    assert client.get("/api/atlas/artifacts/missing.md").status_code == 404


def test_formats_and_structured_document():
    formats = client.get("/api/atlas/formats").json()
    assert formats[0] == {"file": "components.yaml", "schema": "component.schema.json"}

    response = client.get("/api/atlas/model/components.yaml/document").json()
    assert response["file"] == "components.yaml"
    assert response["document"]["components"][0]["id"] == "pg-core"

    document = response["document"]
    document["components"][0]["name"] = "Renamed primary database"
    assert client.put(
        "/api/atlas/model/components.yaml/document", json={"document": document}
    ).status_code == 200
    assert "Renamed primary database" in client.get("/api/atlas/model").json()["files"]["components.yaml"]
    assert client.get("/api/atlas/model/unknown.yaml/document").status_code == 404


def test_import_stage_diff_accept_and_discard():
    assert client.get("/api/atlas/imports").json() == []
    assert client.post("/api/atlas/imports", json={"file": "unknown.yaml", "content": "x"}).status_code == 404

    proposal = "version: 1\ncomponents:\n  - id: imported\n"
    assert client.post(
        "/api/atlas/imports", json={"file": "components.yaml", "content": proposal}
    ).status_code == 200
    assert [item["name"] for item in client.get("/api/atlas/imports").json()] == ["components.yaml"]

    diff = client.get("/api/atlas/imports/components.yaml/diff").json()
    assert diff["file"] == "components.yaml"
    assert diff["changed"] is True
    assert "+  - id: imported" in diff["diff"]
    assert diff["proposed"] == proposal

    assert client.post("/api/atlas/imports/components.yaml/accept").status_code == 200
    model = client.get("/api/atlas/model").json()["files"]
    assert "id: imported" in model["components.yaml"]
    assert client.get("/api/atlas/imports").json() == []
    assert client.get("/api/atlas/imports/components.yaml/diff").status_code == 404

    assert client.post(
        "/api/atlas/imports", json={"file": "risks.yaml", "content": "version: 1\nrisks: []\n"}
    ).status_code == 200
    assert client.delete("/api/atlas/imports/risks.yaml").status_code == 200
    assert client.get("/api/atlas/imports").json() == []


def test_unknown_tool():
    assert client.get("/api/unknown/model").status_code == 404
