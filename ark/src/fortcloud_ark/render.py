"""Generate the backup coverage matrix, restore evidence, and recovery plan."""

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


def _status(asset_id: str, issues: dict[str, list[str]]) -> str:
    return "AT RISK" if issues.get(asset_id) else "PROVEN"


def _age_label(value, today: date, limit: int | None = None) -> str:
    age = core.age_days(value, today)
    if age is None:
        return "missing"
    label = f"{age} d"
    if limit is not None and age > limit:
        return f"**{label} (stale)**"
    return label


def _backup_label(model: dict, asset_id: str) -> str:
    policies = core.backups_for_asset(model, asset_id)
    return ", ".join(f"`{item['id']}`" for item in policies) or "**none**"


def build_coverage(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    p0 = [item for item in model.get("assets", []) if item.get("criticality") == "P0"]
    proven = sum(1 for item in p0 if _status(item["id"], issues) == "PROVEN")
    at_risk = sum(1 for item in model.get("assets", []) if _status(item["id"], issues) == "AT RISK")

    doc = [
        "# Fortcloud Ark — Backup Coverage",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-ark coverage`. Do not edit by hand.",
        "",
        "## Summary",
        "",
        f"- **{len(model.get('assets', []))}** data assets",
        f"- **{len(model.get('backups', []))}** backup policies",
        f"- **{len(model.get('restores', []))}** restore tests",
        f"- **{len(model.get('services', []))}** business services",
        f"- **{proven}/{len(p0)}** P0 assets fully proven",
        f"- **{at_risk}** assets at risk",
        "",
        "**PROVEN** means the asset has a backup policy and at least one recent,",
        "successful restore test compatible with the service targets. See the",
        "[recovery plan](recovery-plan.md) for the gaps.",
        "",
        "## Assets",
        "",
    ]
    rows = []
    for asset in sorted(model.get("assets", []), key=lambda item: (item["criticality"], item["id"])):
        asset_id = asset["id"]
        policies = core.backups_for_asset(model, asset_id)
        restores = core.restores_for_asset(model, asset_id)
        newest_backup = max(policies, key=lambda item: str(item.get("last_successful", ""))) if policies else {}
        newest_restore = max(restores, key=lambda item: str(item.get("last", ""))) if restores else {}
        rto_target, rpo_target = core.targets_for_asset(model, asset_id)
        rows.append(
            [
                f"`{asset_id}` — {escape(asset['name'])}",
                asset.get("criticality", "?"),
                _backup_label(model, asset_id),
                (
                    f"{newest_backup.get('type', '?')} / {newest_backup.get('schedule', '?')}"
                    if policies
                    else "—"
                ),
                f"{newest_backup.get('retention_days', '?')} d" if policies else "—",
                ("yes" if newest_backup.get("immutable") else "**no**") if policies else "—",
                ("yes" if newest_backup.get("cross_region") else "no") if policies else "—",
                _age_label(newest_backup.get("last_successful"), today, core.BACKUP_MAX_AGE_DAYS) if policies else "—",
                (
                    f"{_age_label(newest_restore.get('last'), today, core.RESTORE_MAX_AGE_DAYS)}"
                    f" ({newest_restore.get('result', '?')})"
                    if restores
                    else "**none**"
                ),
                f"{core.format_duration(rto_target)} / {core.format_duration(rpo_target)}",
                _status(asset_id, issues),
            ]
        )
    doc += _table(
        [
            "Asset", "Crit.", "Backup", "Type / Schedule", "Retention",
            "Immutable", "Cross-region", "Last backup", "Last restore", "RTO / RPO", "Status",
        ],
        rows,
    )
    doc += [
        "",
        "## Links",
        "",
        "- [Restore evidence](restore-evidence.md)",
        "- [Recovery plan](recovery-plan.md)",
        "- [Machine-readable status](restore-status.json)",
        "",
    ]
    return "\n".join(doc)


def build_evidence(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    backups = core.backup_map(model)
    assets = core.asset_map(model)
    restores = sorted(model.get("restores", []), key=lambda item: (item.get("backup", ""), item["id"]))

    doc = [
        "# Fortcloud Ark — Restore Evidence",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-ark evidence`. Do not edit by hand.",
        "",
        "Measured values come from the drill record and are compared with the tightest",
        "target of the services using the restored asset.",
        "",
    ]
    rows = []
    for restore in restores:
        backup = backups.get(restore.get("backup"), {})
        asset = assets.get(backup.get("asset"), {})
        asset_id = asset.get("id", "?")
        rto_target, rpo_target = core.targets_for_asset(model, asset_id)
        measured_rto = core.parse_duration(restore.get("measured_rto"))
        measured_rpo = core.parse_duration(restore.get("measured_rpo"))
        rto_ok = rto_target is not None and measured_rto is not None and measured_rto <= rto_target
        rpo_ok = rpo_target is not None and measured_rpo is not None and measured_rpo <= rpo_target
        rows.append(
            [
                f"`{restore['id']}`",
                f"`{asset_id}`",
                core.SCENARIO_LABELS.get(restore.get("scenario"), restore.get("scenario", "?")),
                restore.get("last", "?"),
                _age_label(restore.get("last"), today, core.RESTORE_MAX_AGE_DAYS),
                core.format_duration(measured_rto),
                core.format_duration(rto_target),
                "PASS" if rto_ok else "**FAIL**",
                core.format_duration(measured_rpo),
                core.format_duration(rpo_target),
                "PASS" if rpo_ok else "**FAIL**",
                restore.get("result", "?"),
                restore.get("evidence", "**missing**"),
            ]
        )
    doc += _table(
        [
            "Restore", "Asset", "Scenario", "Date", "Age", "Meas. RTO",
            "Target RTO", "RTO", "Meas. RPO", "Target RPO", "RPO", "Result", "Evidence",
        ],
        rows,
    )

    for asset in sorted(model.get("assets", []), key=lambda item: item["id"]):
        linked = core.restores_for_asset(model, asset["id"])
        if not linked:
            continue
        rto_target, rpo_target = core.targets_for_asset(model, asset["id"])
        doc += [
            "",
            f"## `{asset['id']}` — {escape(asset['name'])}",
            "",
            f"- **Owner:** {asset.get('owner')}",
            f"- **Criticality:** {asset.get('criticality')}",
            f"- **Targets:** RTO {core.format_duration(rto_target)} / "
            f"RPO {core.format_duration(rpo_target)}",
            "",
        ]
        for restore in sorted(linked, key=lambda item: str(item.get("last", "")), reverse=True):
            doc.append(
                f"- `{restore['id']}` — {core.SCENARIO_LABELS.get(restore.get('scenario'), restore.get('scenario'))} "
                f"on {restore.get('last')}: RTO {restore.get('measured_rto')} / "
                f"RPO {restore.get('measured_rpo')}, result **{restore.get('result')}**, "
                f"evidence {restore.get('evidence')}"
            )
            if restore.get("notes"):
                doc.append(f"  - Note: {escape(restore['notes'])}")
        doc.append("")
    doc += [""]
    return "\n".join(doc)


def build_plan(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)

    def rank(asset: dict):
        rto, _ = core.targets_for_asset(model, asset["id"])
        return (0 if asset.get("criticality") == "P0" else 1, rto if rto is not None else 10**9, asset["id"])

    doc = [
        "# Fortcloud Ark — Recovery Plan",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-ark plan`. Do not edit by hand.",
        "",
        "Ordered by asset criticality, then by tightest RTO. Fix the model, not this file.",
        "",
    ]
    for asset in sorted(model.get("assets", []), key=rank):
        asset_id = asset["id"]
        gaps = issues.get(asset_id, [])
        services = ", ".join(
            f"`{item['id']}`" for item in core.services_using_asset(model, asset_id)
        ) or "none"
        rto, rpo = core.targets_for_asset(model, asset_id)
        doc += [
            f"## {asset_id} — {escape(asset['name'])}",
            "",
            f"- **Owner:** {asset.get('owner')}",
            f"- **Criticality:** {asset.get('criticality')}",
            f"- **Services:** {services}",
            f"- **Targets:** RTO {core.format_duration(rto)} / RPO {core.format_duration(rpo)}",
            f"- **Status:** {_status(asset_id, issues)}",
            "",
        ]
        if not gaps:
            doc += ["No gap detected. Keep the backup and restore cadence.", ""]
            continue
        doc += ["**Gaps:**", ""]
        doc += [f"- {gap}." for gap in gaps]
        doc += ["", "**Steps:**", ""]
        for index, gap in enumerate(gaps, start=1):
            sentence = gap[0].upper() + gap[1:] if gap else gap
            doc.append(f"{index}. Fix: {sentence}. Owner: {asset.get('owner')}.")
        doc += [
            f"{len(gaps) + 1}. Re-run `fortcloud-ark check --strict` and attach "
            "`restore-status.json` to the pull request.",
            "",
        ]

    doc += [
        "## Definition of done",
        "",
        "- Every P0 asset has an immutable, encrypted, cross-region backup.",
        "- Backup schedule is compatible with the tightest service RPO.",
        "- Every P0 asset has a recent restore test with a deletion or ransomware scenario.",
        "- Measured RTO and RPO are below the service targets.",
        "- Every restore result is `passed` and has an evidence link.",
        "- `fortcloud-ark check --strict` exits with code 0.",
        "",
    ]
    return "\n".join(doc)


def build_status(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    errors, warnings, issues = validate.analyse(model, today)
    assets = []
    for asset in sorted(model.get("assets", []), key=lambda item: item["id"]):
        asset_id = asset["id"]
        rto, rpo = core.targets_for_asset(model, asset_id)
        restores = core.restores_for_asset(model, asset_id)
        newest = max(restores, key=lambda item: str(item.get("last", ""))) if restores else {}
        assets.append(
            {
                "id": asset_id,
                "criticality": asset.get("criticality"),
                "status": _status(asset_id, issues),
                "backups": len(core.backups_for_asset(model, asset_id)),
                "restore_tests": len(restores),
                "last_restore": newest.get("last"),
                "rto_target_seconds": rto,
                "rpo_target_seconds": rpo,
                "issues": issues.get(asset_id, []),
            }
        )
    payload = {
        "tool": "fortcloud-ark",
        "version": __version__,
        "generated_on": today.isoformat(),
        "summary": {
            "assets": len(model.get("assets", [])),
            "backups": len(model.get("backups", [])),
            "restores": len(model.get("restores", [])),
            "services": len(model.get("services", [])),
            "p0_assets": sum(
                1 for item in model.get("assets", []) if item.get("criticality") == "P0"
            ),
            "assets_at_risk": sum(1 for item in assets if item["status"] == "AT RISK"),
        },
        "assets": assets,
        "errors": errors,
        "warnings": warnings,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write_coverage(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "backup-coverage.md"
    path.write_text(build_coverage(model, today), encoding="utf-8")
    return path


def write_evidence(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "restore-evidence.md"
    path.write_text(build_evidence(model, today), encoding="utf-8")
    return path


def write_plan(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "recovery-plan.md"
    path.write_text(build_plan(model, today), encoding="utf-8")
    return path


def write_status(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "restore-status.json"
    path.write_text(build_status(model, today), encoding="utf-8")
    return path
