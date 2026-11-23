"""French display metadata is served without changing raw identifiers or model data."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "web"))

from api.main import app  # noqa: E402

client = TestClient(app)


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
