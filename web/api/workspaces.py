"""File-backed workspaces: one model and one artifact folder per tool."""

from __future__ import annotations

import difflib
import shutil
from pathlib import Path

import yaml

from . import registry


def ensure_workspace(tool: registry.Tool) -> None:
    tool.model_dir.mkdir(parents=True, exist_ok=True)
    tool.artifact_dir.mkdir(parents=True, exist_ok=True)
    for filename in model_files(tool):
        target = tool.model_dir / filename
        if not target.exists():
            source = tool.example_model_dir / filename
            if source.exists():
                shutil.copyfile(source, target)


def model_files(tool: registry.Tool) -> list[str]:
    return sorted(p.name for p in tool.example_model_dir.glob("*.yaml"))


def read_model(tool: registry.Tool) -> dict[str, str]:
    ensure_workspace(tool)
    return {
        filename: (tool.model_dir / filename).read_text(encoding="utf-8")
        for filename in model_files(tool)
    }


def write_model_file(tool: registry.Tool, filename: str, content: str) -> None:
    if filename not in model_files(tool):
        raise KeyError(f"Unknown model file for {tool.id}: {filename}")
    ensure_workspace(tool)
    (tool.model_dir / filename).write_text(content, encoding="utf-8")


def reset_model(tool: registry.Tool) -> None:
    if tool.model_dir.exists():
        shutil.rmtree(tool.model_dir)
    if tool.artifact_dir.exists():
        shutil.rmtree(tool.artifact_dir)
    ensure_workspace(tool)


def _json_safe(value):
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def read_model_document(tool: registry.Tool, filename: str) -> dict:
    _check_model_name(tool, filename)
    ensure_workspace(tool)
    document = yaml.safe_load((tool.model_dir / filename).read_text(encoding="utf-8")) or {}
    return _json_safe(document)


def write_model_document(tool: registry.Tool, filename: str, document: dict) -> None:
    _check_model_name(tool, filename)
    content = yaml.safe_dump(document, sort_keys=False, allow_unicode=True)
    write_model_file(tool, filename, content)


def import_dir(tool: registry.Tool) -> Path:
    return tool.workspace_dir / "imports"


def import_files(tool: registry.Tool) -> list[str]:
    """List staged proposals whose names match a model file of the tool."""
    path = import_dir(tool)
    if not path.is_dir():
        return []
    known = set(model_files(tool))
    return sorted(entry.name for entry in path.iterdir() if entry.is_file() and entry.name in known)


def _check_model_name(tool: registry.Tool, filename: str) -> None:
    if filename not in model_files(tool):
        raise KeyError(f"Unknown model file for {tool.id}: {filename}")


def read_import(tool: registry.Tool, filename: str) -> str:
    _check_model_name(tool, filename)
    path = import_dir(tool) / filename
    if not path.is_file():
        raise FileNotFoundError(filename)
    return path.read_text(encoding="utf-8")


def stage_import(tool: registry.Tool, filename: str, content: str) -> None:
    _check_model_name(tool, filename)
    import_dir(tool).mkdir(parents=True, exist_ok=True)
    (import_dir(tool) / filename).write_text(content, encoding="utf-8")


def discard_import(tool: registry.Tool, filename: str) -> None:
    _check_model_name(tool, filename)
    (import_dir(tool) / filename).unlink(missing_ok=True)


def import_diff(tool: registry.Tool, filename: str) -> dict:
    proposal = read_import(tool, filename)
    current_path = tool.model_dir / filename
    current = current_path.read_text(encoding="utf-8") if current_path.is_file() else ""
    diff = list(
        difflib.unified_diff(
            current.splitlines(),
            proposal.splitlines(),
            fromfile=f"current/{filename}",
            tofile=f"proposed/{filename}",
            lineterm="",
        )
    )
    return {
        "file": filename,
        "changed": bool(diff),
        "current": current,
        "proposed": proposal,
        "diff": "\n".join(diff),
    }


def accept_import(tool: registry.Tool, filename: str) -> dict[str, str]:
    proposal = read_import(tool, filename)
    write_model_file(tool, filename, proposal)
    discard_import(tool, filename)
    return read_model(tool)


def read_artifact(tool: registry.Tool, filename: str) -> str:
    path = tool.artifact_dir / filename
    if not path.is_file():
        raise FileNotFoundError(filename)
    return path.read_text(encoding="utf-8")


def artifact_records(tool: registry.Tool) -> list[dict]:
    records = []
    for artifact in tool.artifacts:
        path = tool.artifact_dir / artifact.name
        records.append(
            {
                **artifact.__dict__,
                "available": path.is_file(),
                "size": path.stat().st_size if path.is_file() else 0,
            }
        )
    return records
