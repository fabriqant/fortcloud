"""Display-language helpers for the local console API.

English is the source language. Translation resources only override display
labels and prose; identifiers, enum values, file names and model data stay
untouched so every tool keeps validating the same YAML. Diagnostics, API
errors and generated Markdown/Mermaid artifacts are translated at the API
boundary; canonical files on disk remain English.
"""

from __future__ import annotations

import json
import re
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


def _apply_exact(text: str, language: str, filename: str) -> str:
    """Replace whole messages or whole lines using a resource's exact map."""
    if language == DEFAULT_LANGUAGE or not isinstance(text, str) or not text:
        return text
    exact = resource(language, filename).get("exact", {})
    if not isinstance(exact, dict) or not exact:
        return text
    if text in exact and isinstance(exact[text], str):
        return str(exact[text])
    # Artifact resources map many complete lines (headings, table headers,
    # prose paragraphs). Replacing them before regex patterns prevents short
    # phrases from being rewritten inside raw identifiers or model data.
    lines = text.splitlines(keepends=True)
    translated_lines = []
    changed = False
    for line in lines:
        bare = line.rstrip("\r\n")
        ending = line[len(bare) :]
        replacement = exact.get(bare)
        if isinstance(replacement, str):
            translated_lines.append(replacement + ending)
            changed = True
        else:
            translated_lines.append(line)
    return "".join(translated_lines) if changed else text


def _apply_patterns(text: str, language: str, filename: str) -> str:
    """Translate remaining display prose with a resource's regex patterns."""
    if language == DEFAULT_LANGUAGE or not isinstance(text, str) or not text:
        return text
    patterns = resource(language, filename).get("patterns", [])
    if not isinstance(patterns, list) or not patterns:
        return text
    # Longest expressions first: a full sentence must be translated before a
    # shorter phrase it contains, and link labels before their surrounding prose.
    ordered = sorted(
        (item for item in patterns if isinstance(item, dict)),
        key=lambda item: len(str(item.get("match", ""))),
        reverse=True,
    )
    for item in ordered:
        expression = item.get("match")
        replacement = item.get("replace")
        if not isinstance(expression, str) or not isinstance(replacement, str):
            continue
        try:
            text = re.sub(expression, replacement, text)
        except re.error:
            continue
    return text


def translate_text(text: str, language: str, filename: str) -> str:
    """Translate display prose using exact phrases then regex patterns.

    English is the source language, so it bypasses the resource lookup entirely.
    Resources never replace identifiers, enum values, file names or model data:
    each pattern is authored to match only surrounding display prose.
    """
    return _apply_patterns(_apply_exact(text, language, filename), language, filename)


def translate_messages(
    language: str, messages: list[str], filename: str = "diagnostics.json"
) -> list[str]:
    if language == DEFAULT_LANGUAGE:
        return messages
    return [translate_text(message, language, filename) for message in messages]


def translate_error(language: str, message: object) -> object:
    if not isinstance(message, str):
        return message
    return translate_text(message, language, "api_errors.json")


def translate_artifact(language: str, name: str, content: str) -> str:
    if name.lower().endswith(".json"):
        return content
    # Generated reports embed the same deterministic findings returned by the
    # validators. Apply all exact line maps before any regex so a generic
    # diagnostics phrase cannot rewrite an artifact sentence it belongs to.
    text = _apply_exact(content, language, "diagnostics.json")
    text = _apply_exact(text, language, "artifacts.json")
    text = _apply_patterns(text, language, "diagnostics.json")
    return _apply_patterns(text, language, "artifacts.json")


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
