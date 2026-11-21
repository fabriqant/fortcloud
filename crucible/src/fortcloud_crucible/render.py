"""Génération du plan de scénarios, de la matrice des rôles, du plan de communication et du rapport de vérification."""

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


def _label(value, labels: dict) -> str:
    return labels.get(value, "?")


def build_scenarios(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    environments = core.env_map(model)
    scenarios = core.scenario_map(model)

    doc = [
        "# Fortcloud Crucible — Scenario Plan",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-crucible scenarios`. Do not edit by hand.",
        "",
        "Failure drills always start in a controlled environment: isolated,",
        "non-production data and approved. Production needs a passed rehearsal",
        "of the same kind first.",
        "",
    ]
    rows = []
    for scenario in sorted(
        (model.get("scenarios") or {}).get("scenarios", []), key=lambda item: item["id"]
    ):
        sid = scenario["id"]
        environment = environments.get(scenario.get("environment"), {})
        rows.append(
            [
                f"`{sid}` — {escape(scenario['name'])}",
                _label(scenario.get("kind"), core.KIND_LABELS),
                f"`{scenario.get('system')}`",
                f"`{scenario.get('environment')}`",
                "yes" if core.is_controlled(environment) else "no",
                scenario.get("scheduled", "?"),
                _label(scenario.get("status"), core.STATUS_LABELS),
                core.format_duration(core.target_rto_ms(scenario)),
                core.format_duration(core.target_rpo_ms(scenario)),
                core.format_duration(core.scenario_duration(scenario)),
                _status(f"scenario:{sid}", issues),
            ]
        )
    doc += _table(
        ["Scenario", "Kind", "System", "Env", "Controlled", "Scheduled", "Status", "RTO", "RPO", "Window", "Status"],
        rows,
    )

    for scenario in sorted(
        (model.get("scenarios") or {}).get("scenarios", []), key=lambda item: item["id"]
    ):
        gaps = issues.get(f"scenario:{scenario['id']}", [])
        if not gaps:
            continue
        doc += [
            "",
            f"## `{scenario['id']}`",
            "",
            f"- **Owner:** {scenario.get('owner')}",
            f"- **Environment:** `{scenario.get('environment')}`",
        ]
        doc += [f"- **Gap:** {gap}." for gap in gaps]
    doc += ["", "## Links", "", "- [Who does what](roles-matrix.md)", "- [Communication](communication-plan.md)", "- [Verification](verification-report.md)", "- [Machine-readable status](crucible-status.json)", ""]
    return "\n".join(doc)


def build_roles(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    people = core.participant_map(model)

    doc = [
        "# Fortcloud Crucible — Roles Matrix",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-crucible roles`. Do not edit by hand.",
        "",
        "Every exercise names a coordinator, an operator, a communicator and a",
        "verifier. The verifier signs off only after service and data checks pass.",
        "",
    ]
    rows = []
    for scenario in sorted(
        (model.get("scenarios") or {}).get("scenarios", []), key=lambda item: item["id"]
    ):
        sid = scenario["id"]
        cells = [f"`{sid}`"]
        for role in core.REQUIRED_ROLES:
            person = core.person_for_role(model, scenario, role)
            cells.append(f"`{person['id']}`" if person else "**none**")
        cells.append(_status(f"scenario:{sid}", issues))
        rows.append(cells)
    doc += _table(
        ["Scenario", "Coordinator", "Operator", "Communicator", "Verifier", "Status"],
        rows,
    )

    doc += ["", "## Roster", ""]
    doc += _table(
        ["Participant", "Name", "Team", "Contact"],
        [
            [
                f"`{person['id']}`",
                escape(person.get("name", "")),
                person.get("team", "?"),
                person.get("contact", "—"),
            ]
            for person in sorted(people.values(), key=lambda item: item["id"])
        ],
    )
    doc += [""]
    return "\n".join(doc)


def build_communication(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    communication = model.get("communication") or {}
    plan = communication.get("plan") or {}

    doc = [
        "# Fortcloud Crucible — Communication Plan",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-crucible communication`. Do not edit by hand.",
        "",
        "An exercise without communication looks like an incident. Announce the",
        "start, send periodic updates and close the exercise explicitly.",
        "",
        f"- **Update cadence:** {core.format_duration(core.parse_duration(plan.get('updates_every')))}",
        f"- **Escalation:** {plan.get('escalation', '?')}",
        f"- **Go / no-go:** {plan.get('go_no_go', '?')}",
        f"- **Owner:** {plan.get('owner', '?')}",
        "",
        "## Channels",
        "",
    ]
    doc += _table(
        ["Channel", "Name", "Type", "Audience", "Owner", "Status"],
        [
            [
                f"`{channel['id']}`",
                escape(channel.get("name", "")),
                channel.get("type", "?"),
                channel.get("audience", "?"),
                channel.get("owner", "?"),
                _status(f"channel:{channel['id']}", issues),
            ]
            for channel in sorted(communication.get("channels", []), key=lambda item: item["id"])
        ],
    )
    doc += ["", "## Stakeholders", ""]
    doc += _table(
        ["Stakeholder", "Channel", "Notified at", "Status"],
        [
            [
                f"`{item['id']}` — {escape(item.get('name', ''))}",
                f"`{item.get('channel')}`",
                ", ".join(item.get("notify", [])),
                _status(f"stakeholder:{item['id']}", issues),
            ]
            for item in sorted(communication.get("stakeholders", []), key=lambda item: item["id"])
        ],
    )
    for subject in ("communication:coverage", "communication:plan"):
        gaps = issues.get(subject, [])
        if gaps:
            doc += ["", f"## {'Coverage' if subject.endswith('coverage') else 'Plan'} gaps", ""]
            doc += [f"- **Gap:** {gap}." for gap in gaps]
    doc += [""]
    return "\n".join(doc)


def build_verification(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    _, _, issues = validate.analyse(model, today)
    verification = model.get("verification") or {}
    scenarios = core.scenario_map(model)

    doc = [
        "# Fortcloud Crucible — Verification Report",
        "",
        f"> Generated on {today.isoformat()} by `fortcloud-crucible verification`. Do not edit by hand.",
        "",
        "A completed exercise is only credible when both the service and the",
        "data were checked, with evidence and an approved verifier sign-off.",
        "",
        "## Checks",
        "",
    ]
    doc += _table(
        ["Check", "Scenario", "Kind", "Metric", "Expected", "Result", "Status"],
        [
            [
                f"`{check['id']}`",
                f"`{check.get('scenario')}`",
                check.get("kind", "?"),
                check.get("metric", "?"),
                f"`{escape(check.get('expected'))}`",
                check.get("result", "?"),
                _status(f"check:{check['id']}", issues),
            ]
            for check in sorted(verification.get("checks", []), key=lambda item: item["id"])
        ],
    )
    doc += ["", "## Sign-offs", ""]
    doc += _table(
        ["Scenario", "Verifier", "Role", "Date", "Decision", "Status"],
        [
            [
                f"`{signoff.get('scenario')}`",
                f"`{signoff.get('person')}`",
                signoff.get("role", "?"),
                signoff.get("date", "?"),
                signoff.get("decision", "?"),
                _status(f"signoff:{signoff.get('scenario')}", issues),
            ]
            for signoff in sorted(verification.get("signoffs", []), key=lambda item: item["scenario"])
        ],
    )

    doc += ["", "## Exercise verdicts", ""]
    for scenario in sorted(scenarios.values(), key=lambda item: item["id"]):
        sid = scenario["id"]
        checks = core.checks_for_scenario(model, sid)
        kinds = {item.get("kind") for item in checks}
        verdict = (
            "VERIFIED"
            if scenario.get("status") == "passed"
            and {"service", "data"}.issubset(kinds)
            and not issues.get(f"scenario:{sid}")
            else "PENDING"
        )
        doc.append(
            f"- `{sid}` — {_label(scenario.get('status'), core.STATUS_LABELS)}: {verdict}."
        )
    doc += [""]
    return "\n".join(doc)


def build_status(model: dict, today: date | None = None) -> str:
    today = today or date.today()
    errors, warnings, issues = validate.analyse(model, today)
    environments = core.env_map(model)
    scenarios = core.scenario_map(model)

    scenario_rows = []
    for scenario in sorted(scenarios.values(), key=lambda item: item["id"]):
        sid = scenario["id"]
        scenario_rows.append(
            {
                "id": sid,
                "kind": scenario.get("kind"),
                "environment": scenario.get("environment"),
                "controlled_environment": core.is_controlled(
                    environments.get(scenario.get("environment"))
                ),
                "system": scenario.get("system"),
                "scheduled": scenario.get("scheduled"),
                "status": scenario.get("status"),
                "target_rto_ms": core.target_rto_ms(scenario),
                "target_rpo_ms": core.target_rpo_ms(scenario),
                "duration_ms": core.scenario_duration(scenario),
                "roles": {
                    role: (
                        core.person_for_role(model, scenario, role) or {}
                    ).get("id")
                    for role in core.REQUIRED_ROLES
                },
                "checks": {
                    item["id"]: item.get("result")
                    for item in core.checks_for_scenario(model, sid)
                },
                "verification_status": _status(f"scenario:{sid}", issues),
                "issues": issues.get(f"scenario:{sid}", []),
            }
        )

    payload = {
        "tool": "fortcloud-crucible",
        "version": __version__,
        "generated_on": today.isoformat(),
        "summary": {
            "environments": len(environments),
            "controlled_environments": sum(
                1 for item in environments.values() if core.is_controlled(item)
            ),
            "scenarios": len(scenarios),
            "passed": sum(1 for item in scenarios.values() if item.get("status") == "passed"),
            "failed": sum(1 for item in scenarios.values() if item.get("status") == "failed"),
            "planned": sum(1 for item in scenarios.values() if item.get("status") == "planned"),
            "scenarios_at_risk": sum(
                1 for item in scenario_rows if item["verification_status"] == "AT RISK"
            ),
        },
        "scenarios": scenario_rows,
        "errors": errors,
        "warnings": warnings,
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def write_scenarios(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "scenario-plan.md"
    path.write_text(build_scenarios(model, today), encoding="utf-8")
    return path


def write_roles(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "roles-matrix.md"
    path.write_text(build_roles(model, today), encoding="utf-8")
    return path


def write_communication(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "communication-plan.md"
    path.write_text(build_communication(model, today), encoding="utf-8")
    return path


def write_verification(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "verification-report.md"
    path.write_text(build_verification(model, today), encoding="utf-8")
    return path


def write_status(model: dict, output_dir: str | Path = core.DEFAULT_OUTPUT, today=None) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "crucible-status.json"
    path.write_text(build_status(model, today), encoding="utf-8")
    return path
