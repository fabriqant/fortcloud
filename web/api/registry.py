"""Static registry of the seven FortCloud tools."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = ROOT / "web"
REGISTRY_FILE = Path(__file__).with_name("tools.yaml")


@dataclass(frozen=True)
class Artifact:
    name: str
    label: str
    kind: str


@dataclass(frozen=True)
class Tool:
    id: str
    name: str
    tagline: str
    description: str
    accent: str
    icon: str
    artifacts: tuple[Artifact, ...]

    @property
    def source_dir(self) -> Path:
        return ROOT / self.id

    @property
    def src_dir(self) -> Path:
        return self.source_dir / "src"

    @property
    def schema_dir(self) -> Path:
        return self.source_dir / "schema"

    @property
    def example_model_dir(self) -> Path:
        return self.source_dir / "examples" / "hybrid-multicloud" / "model"

    @property
    def workspace_dir(self) -> Path:
        return WEB_ROOT / "workspaces" / self.id

    @property
    def model_dir(self) -> Path:
        return self.workspace_dir / "model"

    @property
    def artifact_dir(self) -> Path:
        return self.workspace_dir / "artifacts"


@lru_cache(maxsize=1)
def load_tools() -> tuple[Tool, ...]:
    data = yaml.safe_load(REGISTRY_FILE.read_text(encoding="utf-8"))
    tools = []
    for item in data["tools"]:
        artifacts = tuple(
            Artifact(
                name=entry["name"],
                label=entry["label"],
                kind=entry["kind"],
            )
            for entry in item.get("artifacts", [])
        )
        tools.append(
            Tool(
                id=item["id"],
                name=item["name"],
                tagline=item["tagline"],
                description=item["description"],
                accent=item.get("accent", "slate"),
                icon=item.get("icon", "box"),
                artifacts=artifacts,
            )
        )
    return tuple(tools)


def get_tool(tool_id: str) -> Tool:
    for tool in load_tools():
        if tool.id == tool_id:
            return tool
    raise KeyError(f"Unknown tool: {tool_id}")


def public_tool(tool: Tool) -> dict:
    return {
        "id": tool.id,
        "name": tool.name,
        "tagline": tool.tagline,
        "description": tool.description,
        "accent": tool.accent,
        "icon": tool.icon,
        "artifacts": [
            {"name": a.name, "label": a.label, "kind": a.kind} for a in tool.artifacts
        ],
    }
