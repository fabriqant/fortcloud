"""Display-language helpers for the local console API.

English is the source language. Translation resources only override display
labels and prose; identifiers, enum values, file names and model data stay
untouched so every tool keeps validating the same YAML.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from fastapi import Request

WEB_ROOT = Path(__file__).resolve().parents[1]
LOCALE_DIR = WEB_ROOT / "i18n"
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "fr")


def normalize_language(value: str | None) -> str:
    if not value:
        return DEFAULT_LANGUAGE
    tag = value.strip().lower().replace("_", "-")
    for language in SUPPORTED_LANGUAGES:
        if tag == language or tag.startswith(f"{language}-"):
            return language
    return DEFAULT_LANGUAGE


def language_from_request(request: Request | None) -> str:
    if request is None:
        return DEFAULT_LANGUAGE
    override = request.query_params.get("lang")
    if override:
        return normalize_language(override)
    return normalize_language(request.headers.get("accept-language", ""))


@lru_cache(maxsize=None)
def resource(language: str, filename: str) -> dict[str, Any]:
    if language == DEFAULT_LANGUAGE:
        return {}
    path = LOCALE_DIR / language / filename
    if not path.is_file():
        return {}
    try:
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text) if path.suffix in {".yaml", ".yml"} else json.loads(text)
    except (OSError, ValueError, yaml.YAMLError):
        return {}
    return data if isinstance(data, dict) else {}


def translate_schema(tool_id: str, filename: str, text: str, language: str) -> str:
    """Translate schema titles only; enum values and keys are data."""
    if language == DEFAULT_LANGUAGE:
        return text
    titles = resource(language, "schemas.json").get("titles", {})
    if not isinstance(titles, dict) or not titles:
        return text
    try:
        document = json.loads(text)
    except ValueError:
        return text

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            title = node.get("title")
            if isinstance(title, str) and title in titles:
                node["title"] = str(titles[title])
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(document)
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"
