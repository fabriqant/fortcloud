"""Named model snapshots and automatic versioning for the console workspaces.

A snapshot is a full copy of a tool's model files under
``workspaces/<tool>/scenarios/<name>/vNNN``.
The current model stays at ``workspaces/<tool>/model`` so every existing route and
the CLIs keep working unchanged. Deleting ``web/workspaces`` removes all scenarios
and snapshots as well.
"""

from __future__ import annotations

import difflib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from . import registry, workspaces

INDEX_FILE = "index.json"
SCENARIO_FILE = "scenario.json"
DEFAULT_SCENARIO = "base"
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_MAX_SNAPSHOTS = 50


class SnapshotError(ValueError):
    """Raised for an invalid scenario name or a missing snapshot."""


def _check_name(name: str) -> str:
    cleaned = name.strip()
    if not _NAME_RE.fullmatch(cleaned):
        raise SnapshotError("A scenario name must be 1-64 letters, digits, dots, underscores or hyphens")
    return cleaned


def scenarios_dir(tool: registry.Tool) -> Path:
    return tool.workspace_dir / "scenarios"


def _scenario_dir(tool: registry.Tool, name: str) -> Path:
    return scenarios_dir(tool) / _check_name(name)


def _index_path(tool: registry.Tool) -> Path:
    return scenarios_dir(tool) / INDEX_FILE


def _read_index(tool: registry.Tool) -> dict:
    path = _index_path(tool)
    if not path.is_file():
        return {"active": DEFAULT_SCENARIO}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"active": DEFAULT_SCENARIO}
    return data if isinstance(data, dict) else {"active": DEFAULT_SCENARIO}


def _write_index(tool: registry.Tool, data: dict) -> None:
    scenarios_dir(tool).mkdir(parents=True, exist_ok=True)
    _index_path(tool).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _metadata(path: Path) -> dict:
    meta_path = path / SCENARIO_FILE
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"description": "", "created_at": "", "updated_at": "", "versions": []}
    result = {
        "description": str(data.get("description", "")),
        "created_at": str(data.get("created_at", "")),
        "updated_at": str(data.get("updated_at", "")),
        "versions": data.get("versions") if isinstance(data.get("versions"), list) else [],
    }
    return result


def _save_metadata(path: Path, meta: dict) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / SCENARIO_FILE).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _copy_files(source: Path, destination: Path, filenames: list[str]) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for filename in filenames:
        candidate = source / filename
        if candidate.is_file():
            shutil.copyfile(candidate, destination / filename)


def _copy_model(tool: registry.Tool, destination: Path) -> None:
    workspaces.ensure_workspace(tool)
    _copy_files(tool.model_dir, destination, workspaces.model_files(tool))


def _ensure_scenario(tool: registry.Tool, name: str, description: str = "") -> Path:
    path = _scenario_dir(tool, name)
    if not (path / SCENARIO_FILE).is_file():
        timestamp = _now()
        meta = {
            "description": description,
            "created_at": timestamp,
            "updated_at": timestamp,
            "versions": [],
        }
        _save_metadata(path, meta)
    return path


def _next_version(versions: list[dict]) -> int:
    numbers = [entry.get("version", 0) for entry in versions if isinstance(entry, dict)]
    return max([0] + [number for number in numbers if isinstance(number, int)]) + 1


def _prune(versions: list[dict], scenario_path: Path) -> list[dict]:
    while len(versions) > _MAX_SNAPSHOTS:
        oldest = versions.pop(0)
        shutil.rmtree(scenario_path / f"v{oldest['version']:03d}", ignore_errors=True)
    return versions


def list_scenarios(tool: registry.Tool) -> dict:
    """List scenarios, their versions and the active scenario name."""
    index = _read_index(tool)
    active = index.get("active", DEFAULT_SCENARIO)
    scenarios = []
    root = scenarios_dir(tool)
    if root.is_dir():
        for path in sorted(root.iterdir()):
            if not path.is_dir() or not (path / SCENARIO_FILE).is_file():
                continue
            meta = _metadata(path)
            scenarios.append(
                {
                    "name": path.name,
                    "description": meta["description"],
                    "created_at": meta["created_at"],
                    "updated_at": meta["updated_at"],
                    "active": path.name == active,
                    "versions": [
                        {
                            "version": entry.get("version"),
                            "label": str(entry.get("label", "")),
                            "created_at": str(entry.get("created_at", "")),
                        }
                        for entry in meta["versions"]
                        if isinstance(entry, dict)
                    ],
                }
            )
    if not any(item["name"] == DEFAULT_SCENARIO for item in scenarios):
        scenarios.insert(
            0,
            {
                "name": DEFAULT_SCENARIO,
                "description": "Bundled example model",
                "created_at": "",
                "updated_at": "",
                "active": active == DEFAULT_SCENARIO,
                "versions": [],
            },
        )
    return {"active": active, "scenarios": scenarios}


def create_scenario(tool: registry.Tool, name: str, description: str = "", activate: bool = True) -> dict:
    """Create a named scenario from the current model without changing it."""
    name = _check_name(name)
    if name == DEFAULT_SCENARIO:
        raise SnapshotError("The base scenario already exists")
    path = _ensure_scenario(tool, name, description)
    meta = _metadata(path)
    timestamp = _now()
    version = _next_version(meta["versions"])
    target = path / f"v{version:03d}"
    _copy_model(tool, target)
    meta["versions"].append({"version": version, "label": "initial", "created_at": timestamp})
    meta["updated_at"] = timestamp
    _save_metadata(path, meta)
    if activate:
        index = _read_index(tool)
        index["active"] = name
        _write_index(tool, index)
    return list_scenarios(tool)


def delete_scenario(tool: registry.Tool, name: str) -> dict:
    name = _check_name(name)
    if name == DEFAULT_SCENARIO:
        raise SnapshotError("The base scenario cannot be deleted")
    shutil.rmtree(_scenario_dir(tool, name), ignore_errors=True)
    index = _read_index(tool)
    if index.get("active") == name:
        workspaces.reset_model(tool)
        index["active"] = DEFAULT_SCENARIO
        _write_index(tool, index)
    return list_scenarios(tool)


def activate_scenario(tool: registry.Tool, name: str) -> dict:
    """Switch the live model folder to a copy of the active version."""
    name = _check_name(name)
    scenarios = list_scenarios(tool)["scenarios"]
    entry = next((item for item in scenarios if item["name"] == name), None)
    if entry is None:
        raise SnapshotError(f"Unknown scenario: {name}")
    if name == DEFAULT_SCENARIO:
        workspaces.reset_model(tool)
    else:
        versions = _metadata(_scenario_dir(tool, name))["versions"]
        if not versions:
            raise SnapshotError("The scenario has no version to activate")
        latest = max(versions, key=lambda item: item.get("version", 0))
        source = _scenario_dir(tool, name) / f"v{latest['version']:03d}"
        _copy_files(source, tool.model_dir, workspaces.model_files(tool))
        # Artifacts belong to the previous model; regenerate them after Check.
        if tool.artifact_dir.exists():
            shutil.rmtree(tool.artifact_dir)
        tool.artifact_dir.mkdir(parents=True, exist_ok=True)
    index = _read_index(tool)
    index["active"] = name
    _write_index(tool, index)
    return list_scenarios(tool)


def snapshot(tool: registry.Tool, label: str = "") -> dict:
    """Record the current model as a new version of the active scenario."""
    index = _read_index(tool)
    name = index.get("active", DEFAULT_SCENARIO)
    path = _ensure_scenario(tool, name)
    meta = _metadata(path)
    timestamp = _now()
    version = _next_version(meta["versions"])
    target = path / f"v{version:03d}"
    _copy_model(tool, target)
    meta["versions"].append(
        {"version": version, "label": label.strip()[:80], "created_at": timestamp}
    )
    meta["updated_at"] = timestamp
    _prune(meta["versions"], path)
    _save_metadata(path, meta)
    return list_scenarios(tool)


def compare(tool: registry.Tool, left: str, right: str) -> dict:
    """Unified diffs of two model versions, or of a version and the live model."""
    def resolve(reference: str) -> tuple[dict[str, str], str]:
        if reference == "current":
            return workspaces.read_model(tool), "current model"
        if ":" in reference:
            name, version_text = reference.split(":", 1)
            path = _scenario_dir(tool, name)
            meta = _metadata(path)
            match = next(
                (
                    entry
                    for entry in meta["versions"]
                    if str(entry.get("version")) == version_text.strip().lstrip("v")
                ),
                None,
            )
            if match is None:
                raise SnapshotError(f"Unknown version: {reference}")
            label = f"{name}/v{match['version']:03d}"
            source = path / f"v{match['version']:03d}"
        else:
            name = reference
            scenarios = list_scenarios(tool)["scenarios"]
            entry = next((item for item in scenarios if item["name"] == name), None)
            if entry is None:
                raise SnapshotError(f"Unknown scenario: {name}")
            if name == DEFAULT_SCENARIO:
                return workspaces.read_model(tool), "base"
            meta = _metadata(_scenario_dir(tool, name))
            if not meta["versions"]:
                raise SnapshotError(f"No version in scenario: {name}")
            match = max(meta["versions"], key=lambda item: item.get("version", 0))
            label = f"{name}/v{match['version']:03d}"
            source = _scenario_dir(tool, name) / f"v{match['version']:03d}"
        return (
            {
                filename: (source / filename).read_text(encoding="utf-8")
                for filename in workspaces.model_files(tool)
                if (source / filename).is_file()
            },
            label,
        )

    left_files, left_label = resolve(left)
    right_files, right_label = resolve(right)
    files = []
    for filename in sorted(set(left_files) | set(right_files)):
        before = left_files.get(filename, "")
        after = right_files.get(filename, "")
        diff = "\n".join(
            difflib.unified_diff(
                before.splitlines(),
                after.splitlines(),
                fromfile=f"{left_label}/{filename}",
                tofile=f"{right_label}/{filename}",
                lineterm="",
            )
        )
        files.append({"file": filename, "changed": bool(diff), "diff": diff})
    return {"left": left_label, "right": right_label, "files": files}
