"""Direct in-process runner for the seven Fortcloud Python packages."""

from __future__ import annotations

import importlib
import sys
import traceback
from types import ModuleType

from . import registry, workspaces

WRITERS = {
    "atlas": ("write_graph", "write_report"),
    "failover": ("write_matrix", "write_plan", "write_drills", "write_status"),
    "ark": ("write_coverage", "write_evidence", "write_plan", "write_status"),
    "ballast": ("write_budget", "write_policies", "write_plan", "write_status"),
    "vitals": ("write_dashboard", "write_signals", "write_plan", "write_status"),
    "custodian": (
        "write_access",
        "write_secrets",
        "write_changes",
        "write_audit",
        "write_status",
    ),
    "crucible": (
        "write_scenarios",
        "write_roles",
        "write_communication",
        "write_verification",
        "write_status",
    ),
}


def load_modules(tool: registry.Tool) -> tuple[ModuleType, ModuleType, ModuleType]:
    source_path = str(tool.src_dir)
    if source_path not in sys.path:
        sys.path.insert(0, source_path)
    prefix = f"fortcloud_{tool.id}"
    core = importlib.import_module(f"{prefix}.core")
    validate = importlib.import_module(f"{prefix}.validate")
    render = importlib.import_module(f"{prefix}.render")
    return core, validate, render


def collect(tool: registry.Tool) -> tuple[dict | None, list[str], list[str]]:
    workspaces.ensure_workspace(tool)
    _, validate, _ = load_modules(tool)
    try:
        return validate.collect(
            tool.model_dir,
            tool.schema_dir,
        )
    except Exception as exc:  # malformed YAML must not kill the API
        detail = "".join(traceback.format_exception_only(type(exc), exc)).strip()
        return None, [detail], []


def validate(tool: registry.Tool, strict: bool = False) -> dict:
    model, errors, warnings = collect(tool)
    ok = not errors and not (strict and warnings)
    return {
        "tool": tool.id,
        "ok": ok,
        "exit_code": 0 if ok else 1,
        "errors": errors,
        "warnings": warnings,
        "strict": strict,
        "model": model,
    }


def check(tool: registry.Tool, strict: bool = False) -> dict:
    result = validate(tool, strict=strict)
    result.pop("model", None)
    if not result["ok"]:
        result["artifacts"] = []
        return result

    model, _, _ = collect(tool)
    if model is None:
        result.update(ok=False, exit_code=1, artifacts=[])
        return result

    _, _, render = load_modules(tool)
    workspaces.ensure_workspace(tool)
    written = []
    for writer_name in WRITERS[tool.id]:
        writer = getattr(render, writer_name)
        path = writer(model, tool.artifact_dir)
        written.append(path.name)
    result["artifacts"] = workspaces.artifact_records(tool)
    return result
