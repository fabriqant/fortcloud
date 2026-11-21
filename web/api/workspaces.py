"""File-backed workspaces: one model and one artifact folder per tool."""

from __future__ import annotations

import shutil
from pathlib import Path

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
