"""Generation of the SLO dashboard, signal catalog, and quality plan."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from . import __version__, core, validate


def escape(value) -> str:
    return str(value).replace('"', "'").replace("\n", " ")


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return lines


def _status(subject: str, issues: dict[str, list[str]]) -> str:
    return "AT RISK" if issues.get(subject) else "OK"


def _target_label(objective: dict) -> str:
    if objective.get("kind") in core.PERCENT_KINDS:
        return f"{core.format_percent(core.parse_percent(objective.get('target')))}%"
    return core.format_duration(core.parse_duration(objective.get("target")))


def _alert_label(objective: dict) -> str:
    if objective.get("kind") in core.PERCENT_KINDS:
        return f"{core.format_percent(core.parse_percent(objective.get('alert_threshold')))}%"
    return core.format_duration(core.parse_duration(objective.get("alert_threshold")))


def _budget_label(metrics: dict) -> str:
    if metrics.get("budget_ms") is not None:
        return core.format_duration_rounded(metrics["budget_ms"])
    if metrics.get("margin_ms") is not None:
        return f"margin {core.format_duration(metrics['margin_ms'])}"
    return "?"


def _headroom_label(metrics: dict) -> str:
    if metrics.get("budget_used") is not None:
        return f"{metrics['budget_used']:.0%} used at alert"
    if metrics.get("margin_ratio") is not None:
        return f"{metrics['margin_ratio']:.0%} margin"
    return "?"


def build_dashboard(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    services = core.service_map(model)
    signals = core.signal_map(model)

    doc = [
        "# FortCloud Vitals — SLO Dashboard",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-vitals dashboard`. Do not edit by hand.",
        "",
        "**Error budget** is the amount of failure a percentile target allows over its",
        "window (for example 99.9% over 30 days = 43m12s). The alert must fire before",
        "that budget is spent.",
        "",
        "## Objectives",
        "",
    ]
    rows = []
    for objective in sorted(model.get("objectives", []), key=lambda item: item["id"]):
        oid = objective["id"]
        service = services.get(objective.get("service"), {})
        signal = signals.get(objective.get("signal"), {})
        metrics = core.objective_metrics(model, objective)
        rows.append(
            [
                f"`{oid}`",
                f"`{objective.get('service')}`",
                service.get("criticality", "?"),
                f"`{objective.get('signal')}`",
                core.KIND_LABELS.get(objective.get("kind"), "?"),
                _target_label(objective),
                core.format_duration(metrics.get("window_ms")),
                _budget_label(metrics),
                _alert_label(objective),
                _headroom_label(metrics),
                core.format_duration(metrics.get("interval_ms")),
                _status(f"objective:{oid}", issues),
            ]
        )
    doc += _table(
        [
            "Objective", "Service", "Crit.", "Signal", "Kind", "Target",
            "Window", "Budget", "Alert at", "Headroom", "Interval", "Status",
        ],
        rows,
    )

    for objective in sorted(model.get("objectives", []), key=lambda item: item["id"]):
        oid = objective["id"]
        service = services.get(objective.get("service"), {})
        signal = signals.get(objective.get("signal"), {})
        metrics = core.objective_metrics(model, objective)
        newest = core.latest_check(model, oid)
        doc += [
            "",
            f"## `{oid}` — {escape(service.get('name', objective.get('service')))}",
            "",
            f"- **Owner:** {objective.get('owner')}",
            f"- **Kind:** {core.KIND_LABELS.get(objective.get('kind'), '?')}",
            f"- **Target / alert:** {_target_label(objective)} / {_alert_label(objective)}",
            f"- **Window:** {core.format_duration(metrics.get('window_ms'))}",
            f"- **Error budget:** {_budget_label(metrics)} — {_headroom_label(metrics)}",
            f"- **Signal:** `{objective.get('signal')}` every "
            f"{core.format_duration(metrics.get('interval_ms'))} "
            f"({core.SOURCE_LABELS.get(signal.get('source'), '?')})",
            f"- **Last check:** {(newest or {}).get('last', 'none')} "
            f"— {(newest or {}).get('result', 'none')}",
            f"- **Status:** {_status(f'objective:{oid}', issues)}",
        ]
        for issue in issues.get(f"objective:{oid}", []):
            doc.append(f"- **Gap:** {issue}.")
        doc.append("")

    doc += [
        "## Links",
        "",
        "- [Signal catalog](signal-catalog.md)",
        "- [Quality plan](quality-plan.md)",
        "- [Machine-readable status](vitals-status.json)",
        "",
    ]
    return "\n".join(doc)


def build_signals(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    objectives = core.objective_map(model)

    doc = [
        "# FortCloud Vitals — Signal Catalog",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-vitals signals`. Do not edit by hand.",
        "",
        "Every signal should back at least one objective. Orphan signals cost money",
        "and produce alerts nobody owns.",
        "",
    ]
    rows = []
    for signal in sorted(model.get("signals", []), key=lambda item: item["id"]):
        sid = signal["id"]
        linked = core.objectives_for_signal(model, sid)
        newest = None
        for objective in linked:
            check = core.latest_check(model, objective["id"])
            if check and (newest is None or str(check.get("last", "")) > str(newest.get("last", ""))):
                newest = check
        rows.append(
            [
                f"`{sid}` — {escape(signal['name'])}",
                core.KIND_LABELS.get(signal.get("kind"), "?"),
                core.SOURCE_LABELS.get(signal.get("source"), "?"),
                core.format_duration(core.parse_duration(signal.get("interval"))),
                signal.get("unit", "?"),
                str(len(linked)),
                (newest or {}).get("last", "—"),
                "OK" if linked else "AT RISK",
            ]
        )
    doc += _table(
        ["Signal", "Kind", "Source", "Interval", "Unit", "Objectives", "Last check", "Status"],
        rows,
    )

    for signal in sorted(model.get("signals", []), key=lambda item: item["id"]):
        if not signal.get("notes"):
            continue
        linked = ", ".join(
            f"`{item['id']}`" for item in core.objectives_for_signal(model, signal["id"])
        ) or "**none**"
        doc += [
            "",
            f"## `{signal['id']}`",
            "",
            f"- **Owner:** {signal.get('owner')}",
            f"- **Objectives:** {linked}",
            f"- **Note:** {escape(signal['notes'])}",
        ]
    doc += [""]
    return "\n".join(doc)


def build_plan(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    services = core.service_map(model)
    signals = core.signal_map(model)

    def rank(objective: dict):
        service = services.get(objective.get("service"), {})
        return (
            0 if service.get("criticality") == "P0" else 1,
            objective["id"],
        )

    doc = [
        "# FortCloud Vitals — Quality Plan",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-vitals plan`. Do not edit by hand.",
        "",
        "Ordered by service criticality. Fix the model, not this file.",
        "",
    ]
    count = 0
    for objective in sorted(model.get("objectives", []), key=rank):
        oid = objective["id"]
        gaps = issues.get(f"objective:{oid}", [])
        for check in core.checks_for_objective(model, oid):
            gaps = gaps + [f"{item}" for item in issues.get(f"check:{check['id']}", [])]
        if not gaps:
            continue
        count += 1
        service = services.get(objective.get("service"), {})
        signal = signals.get(objective.get("signal"), {})
        doc += [
            f"## objective:{oid}",
            "",
            f"- **Owner:** {objective.get('owner')}",
            f"- **Service:** `{objective.get('service')}` ({service.get('criticality', '?')})",
            f"- **Signal:** `{objective.get('signal')}` "
            f"({core.SOURCE_LABELS.get(signal.get('source'), '?')})",
            "",
        ]
        doc += [f"{index}. Fix: {gap[0].upper() + gap[1:]}." for index, gap in enumerate(gaps, 1)]
        doc += [
            f"{len(gaps) + 1}. Re-run `fortcloud-vitals check --strict`.",
            "",
        ]

    if count == 0:
        doc += ["No gap detected. Keep the SLO and verification cadence.", ""]

    doc += [
        "## Definition of done",
        "",
        "- Every P0 service has an availability objective and a data-quality objective.",
        "- Every signal backs at least one objective.",
        "- Each alert fires before the target is breached and before 50% of the error budget is spent.",
        "- Latency and freshness alerts leave at least 20% margin below the target.",
        "- Signal intervals are frequent enough to observe the budget.",
        "- Every objective has a recent check with `result: passed`, evidence and a runbook.",
        "- `fortcloud-vitals check --strict` exits with code 0.",
        "",
    ]
    return "\n".join(doc)


def build_status(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    errors, warnings, issues = validate.analyse(model, today)
    services = core.service_map(model)

    objectives = []
    for objective in sorted(model.get("objectives", []), key=lambda item: item["id"]):
        oid = objective["id"]
        metrics = core.objective_metrics(model, objective)
        newest = core.latest_check(model, oid)
        objectives.append(
            {
                "id": oid,
                "service": objective.get("service"),
                "signal": objective.get("signal"),
                "kind": objective.get("kind"),
                "target": objective.get("target"),
                "alert_threshold": objective.get("alert_threshold"),
                "window_ms": metrics.get("window_ms"),
                "error_budget_ms": (
                    int(metrics["budget_ms"]) if metrics.get("budget_ms") is not None else None
                ),
                "budget_used_at_alert": metrics.get("budget_used"),
                "margin_ratio": metrics.get("margin_ratio"),
                "status": _status(f"objective:{oid}", issues),
                "issues": issues.get(f"objective:{oid}", []),
                "last_check": (newest or {}).get("last"),
                "last_result": (newest or {}).get("result"),
            }
        )

    signals = []
    for signal in sorted(model.get("signals", []), key=lambda item: item["id"]):
        signals.append(
            {
                "id": signal["id"],
                "kind": signal.get("kind"),
                "source": signal.get("source"),
                "interval_ms": core.parse_duration(signal.get("interval")),
                "objectives": len(core.objectives_for_signal(model, signal["id"])),
                "status": (
                    "OK"
                    if core.objectives_for_signal(model, signal["id"])
                    else "AT RISK"
                ),
            }
        )

    payload = {
        "tool": "fortcloud-vitals",
        "version": __version__,
        "generated_on": today.isoformat(),
        "summary": {
            "services": len(model.get("services", [])),
            "signals": len(model.get("signals", [])),
            "objectives": len(model.get("objectives", [])),
            "checks": len(model.get("checks", [])),
            "p0_services": sum(
                1
                for item in model.get("services", [])
                if item.get("criticality") == "P0"
            ),
            "objectives_at_risk": sum(
                1 for item in objectives if item["status"] == "AT RISK"
            ),
        },
        "objectives": objectives,
        "signals": signals,
        "errors": errors,
        "warnings": warnings,
        "services": {
            item["id"]: services[item["id"]].get("criticality")
            for item in model.get("services", [])
        },
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write_dashboard(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "slo-dashboard.md"
    path.write_text(build_dashboard(model, today), encoding="utf-8")
    return path


def write_signals(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "signal-catalog.md"
    path.write_text(build_signals(model, today), encoding="utf-8")
    return path


def write_plan(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "quality-plan.md"
    path.write_text(build_plan(model, today), encoding="utf-8")
    return path


def write_status(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "vitals-status.json"
    path.write_text(build_status(model, today), encoding="utf-8")
    return path
