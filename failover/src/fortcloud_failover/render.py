"""Generation of the coverage matrix, remediation plan and drills."""

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


def _status(strategy_id: str, issues: dict[str, list[str]]) -> str:
    return "AT RISK" if issues.get(strategy_id) else "COVERED"


def _drill_summary(model: dict, today: date, strategy_id: str | None = None) -> tuple[str, str]:
    drills = [
        item
        for item in model.get("drills", [])
        if strategy_id is None or item.get("strategy") == strategy_id
    ]
    if not drills:
        return "none", "**none**"
    newest = max(drills, key=lambda item: str(item.get("last", "")))
    age = core.drill_age_days(newest.get("last"), today)
    label = "missing" if age is None else f"{age} d"
    if age is not None and age > core.DRILL_MAX_AGE_DAYS:
        label = f"**{label} (stale)**"
    if newest.get("result") != "passed":
        label += f" ({newest.get('result')})"
    return label, escape(newest.get("evidence", ""))


def build_matrix(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    components = core.component_map(model)
    strategies = sorted(model.get("strategies", []), key=lambda item: item["id"])
    p0 = [item for item in model.get("topology", []) if item.get("criticality") == "P0"]
    covered_p0 = [item for item in p0 if item["id"] in core.covered_components(model)]
    at_risk = sum(1 for item in strategies if _status(item["id"], issues) == "AT RISK")

    doc = [
        "# Fortcloud Failover — Coverage Matrix",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-failover matrix`. Do not edit by hand.",
        "",
        "## Summary",
        "",
        f"- **{len(model.get('topology', []))}** components in the topology",
        f"- **{len(model.get('services', []))}** business services",
        f"- **{len(strategies)}** failover strategies",
        f"- **{len(covered_p0)}/{len(p0)}** P0 components covered by a strategy",
        f"- **{at_risk}** strategies at risk",
        f"- **{len(model.get('drills', []))}** recorded drills",
        "",
        "A strategy is **COVERED** when no drift check fires. **AT RISK** means at",
        "least one gap must be fixed; see the [remediation plan](failover-plan.md).",
        "",
        "## Strategies",
        "",
    ]
    rows = []
    for strategy in strategies:
        primary = components.get(strategy.get("primary"), {})
        standby = components.get(strategy.get("standby"), {})
        switchover = core.switchover_seconds(strategy)
        rto = core.rto_budget(strategy, model)
        budget = "no service" if rto is None else f"{core.format_duration(switchover)} / {core.format_duration(rto)}"
        drill_label, _ = _drill_summary(model, today, strategy["id"])
        rows.append(
            [
                f"`{strategy['id']}`",
                f"`{strategy.get('primary')}` → `{strategy.get('standby')}`",
                core.MODE_LABELS.get(strategy.get("mode"), strategy.get("mode", "?")),
                f"{primary.get('region', '?')} / {standby.get('region', '?')}",
                strategy.get("replication", "?"),
                budget,
                drill_label,
                _status(strategy["id"], issues),
            ]
        )
    doc += _table(
        ["Strategy", "Primary → Standby", "Mode", "Regions", "Replication", "Switchover / RTO", "Last drill", "Status"],
        rows,
    )

    doc += ["", "## Services and their protection", ""]
    service_rows = []
    for service in sorted(model.get("services", []), key=lambda item: (item["criticality"], item["id"])):
        linked = []
        for component_id in service.get("components", []):
            component = components.get(component_id, {})
            if component.get("criticality") != "P0":
                continue
            covering = [
                item["id"]
                for item in strategies
                if component_id in (item.get("primary"), item.get("standby"))
            ]
            linked.append(f"`{component_id}` → {', '.join(covering) if covering else '**uncovered**'}")
        service_rows.append(
            [
                f"`{service['id']}` — {escape(service['name'])}",
                service.get("criticality", "?"),
                service.get("rto", "?"),
                service.get("rpo", "?"),
                service.get("owner", "?"),
                "; ".join(linked) or "no P0 component",
            ]
        )
    doc += _table(["Service", "Criticality", "RTO", "RPO", "Owner", "P0 coverage"], service_rows)

    doc += [
        "",
        "## Links",
        "",
        "- [Remediation plan](failover-plan.md)",
        "- [Drill scenarios](drill-scenarios.md)",
        "- [Machine-readable status](failover-status.json)",
        "",
    ]
    return "\n".join(doc)


def build_plan(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    services = model.get("services", [])

    def rank(strategy: dict):
        linked = core.services_using(model, strategy.get("primary", ""))
        critical = any(item.get("criticality") == "P0" for item in linked)
        rto = core.rto_budget(strategy, model)
        return (0 if critical else 1, rto if rto is not None else 10**9, strategy["id"])

    doc = [
        "# Fortcloud Failover — Remediation Plan",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-failover plan`. Do not edit by hand.",
        "",
        "Ordered by service criticality, then by tightest RTO. Each gap below comes",
        "from a deterministic rule in `validate.py`; fix the model, not this file.",
        "",
    ]
    for strategy in sorted(model.get("strategies", []), key=rank):
        sid = strategy["id"]
        linked = core.services_using(model, strategy.get("primary", ""))
        names = ", ".join(f"`{item['id']}`" for item in linked) or "none"
        gaps = issues.get(sid, [])
        doc += [
            f"## {sid} — `{strategy.get('primary')}` → `{strategy.get('standby')}`",
            "",
            f"- **Owner:** {strategy.get('owner')}",
            f"- **Services:** {names}",
            f"- **Mode:** {core.MODE_LABELS.get(strategy.get('mode'), strategy.get('mode'))}",
            f"- **Replication:** {strategy.get('replication')}",
            f"- **Status:** {_status(sid, issues)}",
            "",
        ]
        if not gaps:
            doc += [
                "No gap detected. Keep the drill cadence and review the runbook after",
                "every topology change.",
                "",
            ]
            continue
        doc += ["**Gaps:**", ""]
        doc += [f"- {gap}." for gap in gaps]
        doc += ["", "**Steps:**", ""]
        for index, gap in enumerate(gaps, start=1):
            sentence = gap[0].upper() + gap[1:] if gap else gap
            doc.append(f"{index}. Fix: {sentence}. Owner: {strategy.get('owner')}.")
        doc += [
            f"{len(gaps) + 1}. Re-run `fortcloud-failover check --strict` and attach "
            "`failover-status.json` to the pull request.",
            "",
        ]

    if not model.get("strategies"):
        doc.append("No failover strategy declared.")
    doc += [
        "## Definition of done",
        "",
        "- Every P0 component in a service has a strategy with a standby in another region.",
        "- `detection_time + promotion_time` is below the tightest RTO.",
        "- Replication is compatible with the declared RPO.",
        "- A drill younger than 90 days has `result: passed` and an evidence link.",
        "- `fortcloud-failover check --strict` exits with code 0.",
        "",
    ]
    return "\n".join(doc)


def build_drills(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    strategies = sorted(model.get("strategies", []), key=lambda item: item["id"])
    drills = {
        item["id"]: item
        for item in model.get("drills", [])
        if item.get("strategy") in core.strategy_map(model)
    }
    by_strategy = {}
    for item in drills.values():
        by_strategy.setdefault(item["strategy"], []).append(item)

    doc = [
        "# Fortcloud Failover — Drill Scenarios",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-failover drills`. Do not edit by hand.",
        "",
        "Run these scenarios in staging (or in production with an approved change",
        "window). Record the measured time and attach evidence to the pull request.",
        "",
    ]
    rows = []
    for strategy in strategies:
        sid = strategy["id"]
        label, evidence = _drill_summary(model, today, sid)
        rows.append(
            [
                f"`{sid}`",
                f"`{strategy.get('primary')}`",
                f"`{strategy.get('standby')}`",
                core.MODE_LABELS.get(strategy.get("mode"), strategy.get("mode", "?")),
                label,
                evidence or "**missing**",
            ]
        )
    doc += _table(["Strategy", "Primary", "Standby", "Mode", "Last drill", "Evidence"], rows)

    for strategy in strategies:
        sid = strategy["id"]
        primary = strategy.get("primary")
        standby = strategy.get("standby")
        rto = core.rto_budget(strategy, model)
        switchover = core.switchover_seconds(strategy)
        doc += [
            "",
            f"## {sid} — loss of `{primary}`",
            "",
            f"- **Target:** restore service in ≤ {core.format_duration(rto)} "
            f"(expected switchover {core.format_duration(switchover)}).",
            f"- **Replication:** {strategy.get('replication')} — "
            f"verify the RPO before promoting `{standby}`.",
            f"- **Runbook:** {strategy.get('runbook')}",
            "",
            "1. Announce the drill and confirm the change window with the service owner.",
            f"2. Check that the health probe on `{primary}` is green and alerting is active.",
            f"3. Simulate the failure of `{primary}` (stop the endpoint or isolate the region).",
            f"4. Measure detection time against {strategy.get('detection_time')}.",
            f"5. Promote `{standby}` and measure the time against {strategy.get('promotion_time')}.",
            "6. Run a smoke test for every covered service and verify data loss against the RPO.",
            f"7. Fail back to `{primary}`, then record duration, result and evidence in `drills.yaml`.",
            "",
        ]
        recorded = by_strategy.get(sid, [])
        if recorded:
            doc += [
                "Recorded drills:",
                "",
            ]
            for drill in sorted(recorded, key=lambda item: str(item.get("last", "")), reverse=True):
                age = core.drill_age_days(drill.get("last"), today)
                doc.append(
                    f"- `{drill['id']}` — {drill.get('scenario')} on {drill.get('last')} "
                    f"({'missing date' if age is None else str(age) + ' d ago'}, "
                    f"result: {drill.get('result')}) — {drill.get('evidence')}"
                )
        else:
            doc += ["Recorded drills: **none**. Schedule the first one.", ""]
    doc += [""]
    return "\n".join(doc)


def build_status(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    errors, warnings, issues = validate.analyse(model, today)
    strategies = []
    for strategy in sorted(model.get("strategies", []), key=lambda item: item["id"]):
        strategies.append(
            {
                "id": strategy["id"],
                "primary": strategy.get("primary"),
                "standby": strategy.get("standby"),
                "status": _status(strategy["id"], issues),
                "switchover_seconds": core.switchover_seconds(strategy),
                "rto_budget_seconds": core.rto_budget(strategy, model),
                "issues": issues.get(strategy["id"], []),
            }
        )
    payload = {
        "tool": "fortcloud-failover",
        "version": __version__,
        "generated_on": today.isoformat(),
        "summary": {
            "components": len(model.get("topology", [])),
            "services": len(model.get("services", [])),
            "strategies": len(model.get("strategies", [])),
            "drills": len(model.get("drills", [])),
            "p0_components": sum(
                1 for item in model.get("topology", []) if item.get("criticality") == "P0"
            ),
            "covered_p0_components": sum(
                1
                for item in model.get("topology", [])
                if item.get("criticality") == "P0"
                and item["id"] in core.covered_components(model)
            ),
            "strategies_at_risk": sum(
                1 for item in strategies if item["status"] == "AT RISK"
            ),
        },
        "strategies": strategies,
        "errors": errors,
        "warnings": warnings,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write_matrix(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "failover-matrix.md"
    path.write_text(build_matrix(model, today), encoding="utf-8")
    return path


def write_plan(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "failover-plan.md"
    path.write_text(build_plan(model, today), encoding="utf-8")
    return path


def write_drills(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "drill-scenarios.md"
    path.write_text(build_drills(model, today), encoding="utf-8")
    return path


def write_status(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "failover-status.json"
    path.write_text(build_status(model, today), encoding="utf-8")
    return path
