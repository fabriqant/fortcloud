"""Structured view data computed from the same source as the CLI artifacts."""

from __future__ import annotations

import json
import re
from collections import Counter

from . import registry, runner, workspaces

_MERMAID = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)
_DANGER = ("spof", "critical", "failed", "overdue", "blocked", "at_risk")
_WARNING = ("warning", "risk", "single_region", "stale", "partial", "expired")

_KPI_LABELS = {
    "components": "Components",
    "services": "Services",
    "dependencies": "Dependencies",
    "flows": "Flows",
    "risks": "Risks",
    "assets": "Assets",
    "backups": "Backups",
    "restores": "Restores",
    "policies": "Policies",
    "strategies": "Strategies",
    "drills": "Drills",
    "signals": "Signals",
    "objectives": "Objectives",
    "checks": "Checks",
    "principals": "Principals",
    "grants": "Grants",
    "secrets": "Secrets",
    "pipelines": "Pipelines",
    "scenarios": "Scenarios",
    "environments": "Environments",
    "participants": "Participants",
    "spofs": "Single points of failure",
    "critical_risks": "Critical risks",
    "single_region_p0": "P0 in one region",
    "strategies_at_risk": "Strategies at risk",
    "covered_p0_components": "Covered P0 components",
    "p0_components": "P0 components",
}


def _label(key: str) -> str:
    return _KPI_LABELS.get(key, key.replace("_", " ").strip().capitalize())


def _value(item) -> str:
    if item is None:
        return "-"
    if isinstance(item, bool):
        return "Yes" if item else "No"
    if isinstance(item, (list, tuple, set)):
        return ", ".join(str(entry) for entry in item)
    if isinstance(item, dict):
        return json.dumps(item, ensure_ascii=False, sort_keys=True)
    return str(item)


def _table(table_id: str, label: str, rows: list[dict], limit: int = 40) -> dict | None:
    rows = [row for row in rows if isinstance(row, dict)]
    if not rows:
        return None
    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    return {
        "id": table_id,
        "label": label,
        "columns": [{"key": key, "label": _label(key)} for key in columns],
        "rows": [{key: _value(row.get(key)) for key in columns} for row in rows[:limit]],
        "total": len(rows),
    }


def _status_payload(tool: registry.Tool) -> dict:
    for artifact in tool.artifacts:
        if artifact.name.endswith("-status.json"):
            path = tool.artifact_dir / artifact.name
            if path.is_file():
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    return payload if isinstance(payload, dict) else {}
                except (ValueError, OSError):
                    return {}
    return {}


def _counts(model: dict | None) -> dict[str, int]:
    counts: dict[str, int] = {}
    for key, value in (model or {}).items():
        if isinstance(value, list):
            counts[key] = len(value)
        elif isinstance(value, dict):
            counts[key] = sum(len(v) for v in value.values() if isinstance(v, list))
    return counts


def _kpis(summary: dict) -> list[dict]:
    keys = [
        key
        for key, value in summary.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0
    ]
    keys.sort(
        key=lambda key: (
            0 if any(term in key for term in _DANGER) else 1 if any(term in key for term in _WARNING) else 2,
            key,
        )
    )
    result = []
    for key in keys[:4]:
        lowered = key.lower()
        tone = "danger" if any(t in lowered for t in _DANGER) else "warning" if any(t in lowered for t in _WARNING) else "neutral"
        result.append({"label": _label(key), "value": summary[key], "tone": tone, "key": key})
    return result


def _charts(summary: dict) -> list[dict]:
    data = [
        {"name": _label(key), "value": value}
        for key, value in summary.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0
    ]
    if not data:
        return []
    return [
        {
            "id": "summary",
            "label": "Model at a glance",
            "type": "bar",
            "data": data[:10],
        }
    ]


def _graph(tool: registry.Tool) -> str:
    for artifact in tool.artifacts:
        path = tool.artifact_dir / artifact.name
        if not path.is_file():
            continue
        match = _MERMAID.search(path.read_text(encoding="utf-8"))
        if match:
            return match.group(1).strip()
    return ""


def _generic_tables(tool: registry.Tool, model: dict | None, payload: dict) -> list[dict]:
    tables = []
    for key, value in payload.items():
        table = _table(key, _label(key), value) if isinstance(value, list) else None
        if table:
            tables.append(table)
    for key, value in (model or {}).items():
        groups = value.items() if isinstance(value, dict) else [(key, value)]
        for group_key, rows in groups:
            table = _table(f"model-{group_key}", _label(group_key), rows if isinstance(rows, list) else [])
            if table:
                tables.append(table)
    return tables


def _atlas(tool: registry.Tool, model: dict) -> dict:
    core, _, _ = runner.load_modules(tool)
    components = model.get("components", [])
    risks = model.get("risks", [])
    flows = model.get("flows", [])
    dependencies = model.get("dependencies", [])

    spofs = [component for component in components if core.is_spof(component)]
    single_region = [component for component in components if core.is_single_region_p0(component)]
    scored = [(core.severity(core.risk_score(risk)), risk) for risk in risks]
    critical = [risk for label, risk in scored if label == "critical"]

    risks_by_component: dict[str, list[str]] = {}
    for risk in risks:
        for component_id in risk.get("components", []):
            risks_by_component.setdefault(component_id, []).append(risk.get("id", ""))

    summary = {
        "components": len(components),
        "dependencies": len(dependencies),
        "flows": len(flows),
        "risks": len(risks),
        "spofs": len(spofs),
        "critical_risks": len(critical),
        "single_region_p0": len(single_region),
    }

    kpis = [
        {"label": "Single points of failure", "value": len(spofs), "tone": "danger", "key": "spofs"},
        {"label": "Critical risks", "value": len(critical), "tone": "danger", "key": "critical_risks"},
        {"label": "P0 in one region", "value": len(single_region), "tone": "warning", "key": "single_region_p0"},
        {"label": "Components mapped", "value": len(components), "tone": "neutral", "key": "components"},
    ]

    severity_counts = Counter(label for label, _ in scored)
    charts = [
        {
            "id": "risk-severity",
            "label": "Risk severity",
            "type": "bar",
            "data": [
                {"name": name, "value": severity_counts.get(key, 0)}
                for key, name in (
                    ("critical", "Critical"),
                    ("high", "High"),
                    ("moderate", "Moderate"),
                    ("low", "Low"),
                )
            ],
        },
        {
            "id": "criticality",
            "label": "Components by criticality",
            "type": "donut",
            "data": [
                {"name": name, "value": count}
                for name, count in sorted(Counter(c.get("criticality", "") for c in components).items())
            ],
        },
    ]

    spof_rows = [
        {
            "id": component.get("id", ""),
            "name": component.get("name", ""),
            "category": core.CATEGORY_LABELS.get(component.get("category", ""), component.get("category", "")),
            "criticality": component.get("criticality", ""),
            "owner": component.get("owner", ""),
            "risks": ", ".join(risks_by_component.get(component.get("id", ""), [])),
            "action": next(
                (
                    risk.get("action", "")
                    for risk in risks
                    if component.get("id", "") in risk.get("components", [])
                ),
                "",
            ),
        }
        for component in spofs
    ]
    risk_rows = [
        {
            "id": risk.get("id", ""),
            "title": risk.get("title", ""),
            "severity": label,
            "score": core.risk_score(risk),
            "status": risk.get("status", ""),
            "owner": risk.get("owner", ""),
            "action": risk.get("action", ""),
            "target_date": risk.get("target_date", ""),
        }
        for label, risk in scored
    ]
    flow_rows = [
        {
            "id": flow.get("id", ""),
            "name": flow.get("name", ""),
            "criticality": flow.get("criticality", ""),
            "rto": flow.get("rto", ""),
            "rpo": flow.get("rpo", ""),
            "owner": flow.get("owner", ""),
            "last_restore_test": flow.get("last_restore_test", ""),
        }
        for flow in flows
    ]

    tables = [
        table
        for table in (
            _table("spofs", "Single points of failure", spof_rows, limit=20),
            _table("risks", "Risk register", risk_rows, limit=30),
            _table("flows", "Business flows", flow_rows, limit=20),
        )
        if table
    ]
    return {
        "summary": summary,
        "kpis": kpis,
        "charts": charts,
        "tables": tables,
        "graph": _graph(tool),
    }


def build(tool: registry.Tool, model: dict | None) -> dict:
    payload = _status_payload(tool)
    if tool.id == "atlas" and model:
        return _atlas(tool, model)
    summary = dict(payload.get("summary") or _counts(model))
    return {
        "summary": summary,
        "kpis": _kpis(summary),
        "charts": _charts(summary),
        "tables": _generic_tables(tool, model, payload),
        "graph": _graph(tool),
    }
