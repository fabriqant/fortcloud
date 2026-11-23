"""French display metadata is served without changing raw identifiers or model data."""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "web"))

from api import i18n, registry, workspaces  # noqa: E402
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


def test_tools_default_to_english_and_follow_accept_language() -> None:
    english = client.get("/api/tools").json()
    french = client.get("/api/tools", headers={"Accept-Language": "fr-FR,fr;q=0.9"}).json()

    assert [tool["id"] for tool in english] == [tool["id"] for tool in french]
    assert english[0]["tagline"] == "Map dependencies. See risk."
    assert french[0]["tagline"] == "Cartographiez les dépendances. Visualisez les risques."
    assert french[0]["name"] == "FortCloud Atlas"
    assert french[0]["artifacts"][0]["name"] == "dependency-graph.md"


def test_query_language_overrides_header() -> None:
    french = client.get("/api/tools?lang=fr", headers={"Accept-Language": "en"}).json()
    assert french[0]["description"].startswith("Atlas modélise les dépendances")


def test_schema_titles_are_translated_but_enum_values_are_not() -> None:
    schemas = client.get("/api/atlas/schemas?lang=fr").json()
    documents = [json.loads(value) for value in schemas.values()]
    titles = {document.get("title") for document in documents if document.get("title")}

    assert "Inventaire des composants" in titles
    assert "Component inventory" not in titles

    component = next(document for document in documents if document.get("title") == "Inventaire des composants")
    properties = component["properties"]["components"]["items"]["properties"]
    assert "criticality" in properties
    assert "P0" in properties["criticality"]["enum"]


def test_connector_metadata_is_translated_without_touching_identifiers() -> None:
    french = client.get("/api/connectors", headers={"Accept-Language": "fr"}).json()
    aws = next(provider for provider in french if provider["id"] == "aws")
    profile = next(field for field in aws["fields"] if field["name"] == "profile")

    assert aws["label"] == "AWS"
    assert profile["label"] == "Profil AWS"
    assert profile["placeholder"] == "my-profile"
    assert profile["discovery"] == "aws_profiles"


def test_ui_locale_files_have_the_same_flat_keys() -> None:
    en_dir = ROOT / "web" / "ui" / "src" / "locales" / "en"
    fr_dir = ROOT / "web" / "ui" / "src" / "locales" / "fr"
    pairs = [
        (ROOT / "web" / "ui" / "src" / "locales" / "en.json", ROOT / "web" / "ui" / "src" / "locales" / "fr.json"),
        *[(en_dir / path.name, fr_dir / path.name) for path in sorted(en_dir.glob("*.json"))],
    ]

    assert pairs
    for english_path, french_path in pairs:
        english = json.loads(english_path.read_text(encoding="utf-8"))
        french = json.loads(french_path.read_text(encoding="utf-8"))
        assert set(english) == set(french), english_path.name
        assert all(isinstance(value, str) for value in english.values())
        assert all(isinstance(value, str) for value in french.values())


def test_display_translation_resources_have_a_valid_shape() -> None:
    for filename in ("diagnostics.json", "api_errors.json", "artifacts.json"):
        data = i18n.resource("fr", filename)
        assert set(data) == {"exact", "patterns"}, filename
        assert data["exact"] and data["patterns"], filename
        assert all(isinstance(value, str) for value in data["exact"].values())
        for pattern in data["patterns"]:
            assert isinstance(pattern["match"], str)
            assert isinstance(pattern["replace"], str)
            re.compile(pattern["match"])


def test_validation_findings_follow_the_request_language() -> None:
    english = client.post("/api/atlas/validate?strict=true").json()
    french = client.post("/api/atlas/validate?strict=true&lang=fr").json()

    assert english["warnings"]
    assert "last restore test" in english["warnings"][0]
    assert "dernier test de restauration" in french["warnings"][0]
    assert "last restore test" not in french["warnings"][0]


def test_api_error_details_are_translated() -> None:
    english = client.get("/api/atlas/artifacts/missing.md").json()
    french = client.get("/api/atlas/artifacts/missing.md?lang=fr").json()

    french_header = client.get(
        "/api/atlas/artifacts/missing.md", headers={"Accept-Language": "fr-FR,fr;q=0.9"}
    ).json()

    assert english["detail"] == "Artifact not generated: missing.md"
    assert french["detail"] == "Artefact non généré : missing.md"
    assert french_header == french


def test_markdown_artifacts_are_translated_at_read_time() -> None:
    client.post("/api/atlas/check")
    english = client.get("/api/atlas/artifacts/resilience-report.md").json()["content"]
    french = client.get("/api/atlas/artifacts/resilience-report.md?lang=fr").json()["content"]

    assert "# FortCloud Atlas — Resilience Report" in english
    assert "# FortCloud Atlas — Rapport de résilience" in french
    assert "| Catégorie |" in french
    assert "R-002" in french
    assert "P0" in french
    assert client.get("/api/atlas/artifacts/resilience-report.md").json()["content"] == english


def test_ballast_generated_labels_are_translated_without_changing_values() -> None:
    client.post("/api/ballast/check")
    policy = client.get("/api/ballast/artifacts/policy-matrix.md?lang=fr").json()["content"]
    plan = client.get("/api/ballast/artifacts/resilience-plan.md?lang=fr").json()["content"]
    budget = client.get("/api/ballast/artifacts/timeout-budget.md?lang=fr").json()["content"]

    assert "- **Disjoncteur :** après 5 échecs, réinitialisation 1m" in policy
    assert "jitter : non" in policy
    assert "jitter : oui" in policy
    assert "after 5" not in policy
    assert not re.search(r"jitter : no\b", policy)
    assert "pire cas" in plan
    assert "worst case" not in plan
    assert "du budget" in budget
    assert "of budget" not in budget


def test_vitals_generated_prose_is_translated_without_changing_results() -> None:
    client.post("/api/vitals/check")
    french = client.get("/api/vitals/artifacts/slo-dashboard.md?lang=fr").json()["content"]

    assert "fenêtre (par exemple 99,9 % sur 30 jours = 43m12s)" in french
    assert "marge de 1m" in french
    assert "20 % de marge" in french
    assert "margin" not in french
    assert "passed" in french


def test_structured_graph_labels_are_translated_without_changing_ids() -> None:
    client.post("/api/atlas/check")
    french = client.get("/api/atlas/data?lang=fr").json()

    assert french["graph"].startswith("flowchart LR")
    assert "Réseau" in french["graph"]
    assert "Stockage" in french["graph"]
    assert "dns-global" in french["graph"]
    assert "pg-core" in french["graph"]


def test_json_status_artifacts_stay_in_english() -> None:
    client.post("/api/ark/check")
    english = client.get("/api/ark/artifacts/restore-status.json").json()["content"]
    french = client.get("/api/ark/artifacts/restore-status.json?lang=fr").json()["content"]

    assert english == french
    assert "PROVEN" in french or "AT RISK" in french
