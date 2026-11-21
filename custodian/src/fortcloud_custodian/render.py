"""Génération des matrices d'accès, d'inventaire, de contrôle des changements et d'audit."""

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


def _age(value, today: date) -> str:
    days = value
    if days is None:
        return "?"
    return f"{days}d"


def build_access(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    environments = core.env_map(model)
    principals = core.principal_map(model)

    doc = [
        "# Fortcloud Custodian — Access Matrix",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-custodian access`. Do not edit by hand.",
        "",
        "Least privilege means explicit permissions, one environment per identity,",
        "a reason for elevated roles and an expiry date on every grant.",
        "",
    ]
    rows = []
    for grant in sorted(
        (model.get("access") or {}).get("grants", []), key=lambda item: item["id"]
    ):
        gid = grant["id"]
        principal = principals.get(grant.get("principal"), {})
        remaining = core.days_until(grant.get("expires"), today)
        rows.append(
            [
                f"`{gid}`",
                f"`{grant.get('principal')}`",
                core.PRINCIPAL_LABELS.get(principal.get("type"), "?"),
                f"`{grant.get('environment')}`",
                core.CLASSIFICATION_LABELS.get(
                    environments.get(grant.get("environment"), {}).get("classification"), "?"
                ),
                grant.get("role", "?"),
                str(len(grant.get("permissions", []))),
                grant.get("expires", "**none**"),
                "expired" if remaining is not None and remaining < 0 else "active",
                _status(f"grant:{gid}", issues),
            ]
        )
    doc += _table(
        [
            "Grant", "Principal", "Type", "Environment", "Class.",
            "Role", "# Perms", "Expires", "Term", "Status",
        ],
        rows,
    )

    doc += ["", "## Environments", ""]
    doc += _table(
        ["Environment", "Classification", "Owner", "Principals", "Grants", "Secrets", "Pipelines"],
        [
            [
                f"`{env_id}` — {escape(info.get('name', env_id))}",
                core.CLASSIFICATION_LABELS.get(info.get("classification"), "?"),
                info.get("owner", "?"),
                str(
                    sum(
                        env_id in item.get("environments", [])
                        for item in principals.values()
                    )
                ),
                str(len(core.grants_for_environment(model, env_id))),
                str(len(core.secrets_for_environment(model, env_id))),
                str(len(core.pipelines_for_environment(model, env_id))),
            ]
            for env_id, info in sorted(environments.items())
        ],
    )

    doc += ["", "## Elevated and broad grants", ""]
    flagged = 0
    for grant in sorted(
        (model.get("access") or {}).get("grants", []), key=lambda item: item["id"]
    ):
        elevated = core.is_elevated(grant.get("role"))
        broad = len(grant.get("permissions", [])) > core.MAX_PERMISSIONS
        if not (elevated or broad):
            continue
        flagged += 1
        doc += [
            f"- `{grant['id']}` — role `{grant.get('role')}`, "
            f"{len(grant.get('permissions', []))} permissions, expires {grant.get('expires', 'never')}.",
        ]
        for issue in issues.get(f"grant:{grant['id']}", []):
            doc.append(f"  - **Gap:** {issue}.")
    if not flagged:
        doc += ["No elevated or over-broad grant detected."]
    doc += ["", "## Links", "", "- [Secret inventory](secret-inventory.md)", "- [Change control](change-control.md)", "- [Machine-readable status](custodian-status.json)", ""]
    return "\n".join(doc)


def build_secrets(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)

    doc = [
        "# Fortcloud Custodian — Secret Inventory",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-custodian secrets`. Do not edit by hand.",
        "",
        "Only **references** belong in this model. A secret shared between",
        "environments, especially with production, breaks isolation.",
        "",
    ]
    rows = []
    for secret in sorted(model.get("secrets", []), key=lambda item: item["id"]):
        sid = secret["id"]
        rows.append(
            [
                f"`{sid}` — {escape(secret['name'])}",
                core.STORE_LABELS.get(secret.get("store"), "?"),
                f"`{escape(secret.get('reference'))}`",
                ", ".join(f"`{env}`" for env in secret.get("environments", [])),
                secret.get("last_rotated", "?"),
                _age(core.secret_age_days(secret, today), today),
                f"{secret.get('rotation_days')}d",
                str(len(secret.get("used_by", []))),
                _status(f"secret:{sid}", issues),
            ]
        )
    doc += _table(
        ["Secret", "Store", "Reference", "Environments", "Last rotated", "Age", "Policy", "Users", "Status"],
        rows,
    )

    for secret in sorted(model.get("secrets", []), key=lambda item: item["id"]):
        gaps = issues.get(f"secret:{secret['id']}", [])
        if not gaps:
            continue
        doc += [
            "",
            f"## `{secret['id']}`",
            "",
            f"- **Owner:** {secret.get('owner')}",
            f"- **Reference:** `{escape(secret.get('reference'))}`",
        ]
        doc += [f"- **Gap:** {gap}." for gap in gaps]
    doc += [""]
    return "\n".join(doc)


def build_changes(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)

    doc = [
        "# Fortcloud Custodian — Change Control",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-custodian changes`. Do not edit by hand.",
        "",
        "A restricted environment requires a peer review, unit and integration",
        "tests, an identified deployer and a verified, automated rollback.",
        "",
    ]
    rows = []
    for pipeline in sorted(model.get("changes", []), key=lambda item: item["id"]):
        pid = pipeline["id"]
        review = pipeline.get("review") or {}
        rollback = pipeline.get("rollback") or {}
        rows.append(
            [
                f"`{pid}` — {escape(pipeline['name'])}",
                f"`{pipeline.get('environment')}`",
                pipeline.get("trigger", "?"),
                f"`{pipeline.get('deployer')}`",
                "yes" if review.get("required") else "**no**",
                str(review.get("approvers", 0)),
                ", ".join(pipeline.get("tests", [])),
                "yes" if rollback.get("enabled") else "**no**",
                "auto" if rollback.get("automate") else "manual",
                _status(f"pipeline:{pid}", issues),
            ]
        )
    doc += _table(
        ["Pipeline", "Env", "Trigger", "Deployer", "Review", "Approvers", "Tests", "Rollback", "Mode", "Status"],
        rows,
    )

    for pipeline in sorted(model.get("changes", []), key=lambda item: item["id"]):
        gaps = issues.get(f"pipeline:{pipeline['id']}", [])
        if not gaps:
            continue
        doc += [
            "",
            f"## `{pipeline['id']}`",
            "",
            f"- **Owner:** {pipeline.get('owner')}",
            f"- **Environment:** `{pipeline.get('environment')}`",
        ]
        doc += [f"- **Gap:** {gap}." for gap in gaps]
    doc += ["", "Every remediation means editing the model and re-running `fortcloud-custodian check`.", ""]
    return "\n".join(doc)


def build_audit(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    audit = model.get("audit") or {}

    doc = [
        "# Fortcloud Custodian — Audit Trail",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-custodian audit`. Do not edit by hand.",
        "",
        "Sensitive operations must leave durable evidence. A log that can be",
        "edited is not an audit trail.",
        "",
        "## Log sinks",
        "",
    ]
    doc += _table(
        ["Sink", "Type", "Destination", "Retention", "Immutable", "Status"],
        [
            [
                f"`{sink['id']}`",
                sink.get("type", "?"),
                f"`{escape(sink.get('destination'))}`",
                f"{sink.get('retention_days')}d",
                "yes" if sink.get("immutable") else "**no**",
                _status(f"sink:{sink['id']}", issues),
            ]
            for sink in sorted(audit.get("sinks", []), key=lambda item: item["id"])
        ],
    )
    doc += ["", "## Sensitive operations", ""]
    doc += _table(
        ["Operation", "Kind", "Environment", "Logged", "Sink", "Last evidence", "Status"],
        [
            [
                f"`{op['id']}` — {escape(op['name'])}",
                op.get("kind", "?"),
                f"`{op.get('environment')}`",
                "yes" if op.get("logged") else "**no**",
                f"`{op.get('sink', '—')}`",
                op.get("last_evidence", "—"),
                _status(f"operation:{op['id']}", issues),
            ]
            for op in sorted(audit.get("operations", []), key=lambda item: item["id"])
        ],
    )
    gaps = issues.get("audit:coverage", [])
    if gaps:
        doc += ["", "## Coverage gaps", ""] + [f"- **Gap:** {gap}." for gap in gaps]
    doc += [""]
    return "\n".join(doc)


def build_status(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    errors, warnings, issues = validate.analyse(model, today)
    principals = core.principal_map(model)
    environments = core.env_map(model)

    grants = []
    for grant in sorted(
        (model.get("access") or {}).get("grants", []), key=lambda item: item["id"]
    ):
        gid = grant["id"]
        grants.append(
            {
                "id": gid,
                "principal": grant.get("principal"),
                "principal_type": principals.get(grant.get("principal"), {}).get("type"),
                "environment": grant.get("environment"),
                "classification": environments.get(grant.get("environment"), {}).get("classification"),
                "role": grant.get("role"),
                "permission_count": len(grant.get("permissions", [])),
                "expires": grant.get("expires"),
                "days_remaining": core.days_until(grant.get("expires"), today),
                "status": _status(f"grant:{gid}", issues),
                "issues": issues.get(f"grant:{gid}", []),
            }
        )

    secrets = []
    for secret in sorted(model.get("secrets", []), key=lambda item: item["id"]):
        sid = secret["id"]
        secrets.append(
            {
                "id": sid,
                "store": secret.get("store"),
                "environments": secret.get("environments", []),
                "age_days": core.secret_age_days(secret, today),
                "rotation_days": secret.get("rotation_days"),
                "status": _status(f"secret:{sid}", issues),
                "issues": issues.get(f"secret:{sid}", []),
            }
        )

    pipelines = []
    for pipeline in sorted(model.get("changes", []), key=lambda item: item["id"]):
        pid = pipeline["id"]
        rollback = pipeline.get("rollback") or {}
        pipelines.append(
            {
                "id": pid,
                "environment": pipeline.get("environment"),
                "review_required": (pipeline.get("review") or {}).get("required"),
                "approvers": (pipeline.get("review") or {}).get("approvers"),
                "tests": pipeline.get("tests", []),
                "rollback_enabled": rollback.get("enabled"),
                "rollback_automated": rollback.get("automate"),
                "rollback_age_days": core.rollback_age_days(pipeline, today),
                "status": _status(f"pipeline:{pid}", issues),
                "issues": issues.get(f"pipeline:{pid}", []),
            }
        )

    operations = []
    for operation in sorted(
        (model.get("audit") or {}).get("operations", []), key=lambda item: item["id"]
    ):
        oid = operation["id"]
        operations.append(
            {
                "id": oid,
                "kind": operation.get("kind"),
                "environment": operation.get("environment"),
                "logged": operation.get("logged"),
                "sink": operation.get("sink"),
                "evidence_age_days": core.evidence_age_days(operation, today),
                "status": _status(f"operation:{oid}", issues),
                "issues": issues.get(f"operation:{oid}", []),
            }
        )

    payload = {
        "tool": "fortcloud-custodian",
        "version": __version__,
        "generated_on": today.isoformat(),
        "summary": {
            "environments": len(environments),
            "principals": len(principals),
            "grants": len(grants),
            "secrets": len(secrets),
            "pipelines": len(pipelines),
            "sinks": len((model.get("audit") or {}).get("sinks", [])),
            "operations": len(operations),
            "restricted_environments": sum(
                1
                for info in environments.values()
                if info.get("classification") == core.RESTRICTED
            ),
            "entities_at_risk": sum(
                1
                for group in (grants, secrets, pipelines, operations)
                for item in group
                if item["status"] == "AT RISK"
            ),
        },
        "grants": grants,
        "secrets": secrets,
        "pipelines": pipelines,
        "operations": operations,
        "errors": errors,
        "warnings": warnings,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write_access(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "access-matrix.md"
    path.write_text(build_access(model, today), encoding="utf-8")
    return path


def write_secrets(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "secret-inventory.md"
    path.write_text(build_secrets(model, today), encoding="utf-8")
    return path


def write_changes(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "change-control.md"
    path.write_text(build_changes(model, today), encoding="utf-8")
    return path


def write_audit(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "audit-trail.md"
    path.write_text(build_audit(model, today), encoding="utf-8")
    return path


def write_status(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "custodian-status.json"
    path.write_text(build_status(model, today), encoding="utf-8")
    return path
