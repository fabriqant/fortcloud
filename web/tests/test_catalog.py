"""Tests for the local reference-value catalog used by guided forms."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "web"))

from api import catalog  # noqa: E402
from api.main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_catalog(tmp_path: Path):
    """Use a temporary SQLite file so tests never touch the user's catalog."""
    original = catalog.DB_PATH
    catalog.DB_PATH = tmp_path / "catalog.sqlite3"
    yield
    catalog.DB_PATH = original


def test_defaults_are_seeded():
    values = client.get("/api/catalog").json()

    assert list(values) == list(catalog.CATEGORIES)
    assert "sec-team" in values["owners"]
    assert "net-team" in values["teams"]
    assert "eu-west-3" in values["regions"]
    assert "az1" in values["zones"]
    assert "single SaaS" in values["providers"]
    assert "single DNS provider" in values["providers"]
    assert "prod" in values["environments"]
    assert "checkout" in values["services"]

    # The fixture database was created on demand.
    assert catalog.DB_PATH.is_file()


def test_add_rename_and_remove_a_value():
    added = client.post("/api/catalog", json={"category": "owners", "value": "qa-team"})
    assert added.status_code == 200
    assert added.json()["added"] is True
    assert "qa-team" in client.get("/api/catalog").json()["owners"]

    duplicate = client.post("/api/catalog", json={"category": "owners", "value": " qa-team "})
    assert duplicate.json()["added"] is False

    renamed = client.patch(
        "/api/catalog",
        json={"category": "owners", "value": "qa-team", "new_value": "quality-team"},
    )
    assert renamed.json()["renamed"] is True
    owners = client.get("/api/catalog").json()["owners"]
    assert "quality-team" in owners
    assert "qa-team" not in owners

    removed = client.request(
        "DELETE", "/api/catalog", json={"category": "owners", "value": "quality-team"}
    )
    assert removed.json()["removed"] is True
    assert "quality-team" not in client.get("/api/catalog").json()["owners"]


def test_invalid_category_and_empty_value_are_rejected():
    assert client.get("/api/catalog").status_code == 200
    invalid = client.post("/api/catalog", json={"category": "colors", "value": "blue"})
    assert invalid.status_code == 400
    empty = client.post("/api/catalog", json={"category": "owners", "value": "   "})
    assert empty.status_code == 400
