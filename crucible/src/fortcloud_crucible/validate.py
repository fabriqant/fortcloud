"""Validation structurelle et sémantique du modèle Fortcloud Crucible."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from jsonschema import Draft202012Validator

from . import core


def schema_errors(model_dir: Path, schema_dir: Path | None = None) -> list[str]:
    errors: list[str] = []
    for key, (filename, _) in core.FILES.items():
        path = Path(model_dir) / filename
        if not path.exists():
            errors.append(f"{filename}: file missing")
            continue
        try:
            document = core.load_yaml(path)
            schema = core.load_schema(key, schema_dir)
        except (OSError, ValueError) as exc:
            errors.append(f"{filename}: {exc}")
            continue
        validator = Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
            location = "/".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{filename} [{location}]: {error.message}")
    return errors


def _check_duplicates(items: list[dict], label: str, key: str, errors: list[str]) -> None:
    counts = Counter(item.get(key) for item in items)
    for identifier, count in counts.items():
        if count > 1:
            errors.append(f"{label}: identifier '{identifier}' used {count} times")


def analyse(
    model: dict, today: date | None = None
) -> tuple[list[str], list[str], dict[str, list[str]]]:
    """Return (errors, warnings, issues keyed by entity)."""
    today = today or date.today()
    errors: list[str] = []
    warnings: list[str] = []
    issues: dict[str, list[str]] = defaultdict(list)

    environments = model.get("environments") or []
    scenarios_doc = model.get("scenarios") or {}
    participants = scenarios_doc.get("participants") or []
    scenarios = scenarios_doc.get("scenarios") or []
    communication = model.get("communication") or {}
    channels = communication.get("channels") or []
    stakeholders = communication.get("stakeholders") or []
    plan = communication.get("plan") or {}
    verification = model.get("verification") or {}
    checks = verification.get("checks") or []
    signoffs = verification.get("signoffs") or []

    for items, label, key in (
        (environments, "environments", "id"),
        (participants, "participants", "id"),
        (scenarios, "scenarios", "id"),
        (channels, "channels", "id"),
        (stakeholders, "stakeholders", "id"),
        (checks, "checks", "id"),
        (signoffs, "signoffs", "scenario"),
    ):
        _check_duplicates(items, label, key, errors)

    envs = core.env_map(model)
    people = core.participant_map(model)
    scenario_index = core.scenario_map(model)
    channel_index = core.channel_map(model)
    signoff_index = core.signoff_map(model)

    # Environments — only isolated, non-production, approved ones are controlled.
    for environment in environments:
        eid = environment["id"]
        if not environment.get("approved"):
            message = "environment is not approved for exercises"
            warnings.append(f"environment {eid}: {message}")
            issues[f"environment:{eid}"].append(message)

    # Scenarios — controlled first, explicit roles, measurable targets.
    for scenario in scenarios:
        sid = scenario["id"]
        subject = f"scenario:{sid}"
        environment = scenario.get("environment")
        env = envs.get(environment)
        if env is None:
            message = f"unknown environment '{environment}'"
            errors.append(f"scenario {sid}: {message}")
            issues[subject].append(message)
        elif not core.is_controlled(env):
            evidence = core.controlled_first_evidence(model, scenario)
            if evidence is None:
                message = (
                    f"no passed '{scenario.get('kind')}' exercise in a controlled "
                    "environment — rehearse there first"
                )
                errors.append(f"scenario {sid}: {message}")
                issues[subject].append(message)

        if scenario.get("channel") not in channel_index:
            message = f"communication channel '{scenario.get('channel')}' not found"
            errors.append(f"scenario {sid}: {message}")
            issues[subject].append(message)

        roles = [item.get("role") for item in scenario.get("assignments", [])]
        for role in core.REQUIRED_ROLES:
            if role not in roles:
                message = f"no '{role}' assigned to this exercise"
                errors.append(f"scenario {sid}: {message}")
                issues[subject].append(message)
        for assignment in scenario.get("assignments", []):
            person = assignment.get("person")
            if person not in people:
                message = f"participant '{person}' not found"
                errors.append(f"scenario {sid}: {message}")
                issues[subject].append(message)

        for field in ("target_rto", "target_rpo", "duration"):
            if core.parse_duration(scenario.get(field)) is None:
                message = f"invalid duration '{scenario.get(field)}' in {field}"
                errors.append(f"scenario {sid}: {message}")
                issues[subject].append(message)

        length = core.scenario_duration(scenario)
        if length is not None and length > core.MAX_EXERCISE_DURATION_MS:
            message = (
                f"exercise window {core.format_duration(length)} exceeds "
                f"{core.format_duration(core.MAX_EXERCISE_DURATION_MS)}"
            )
            warnings.append(f"scenario {sid}: {message}")
            issues[subject].append(message)

        status = scenario.get("status")
        scheduled_age = core.age_days(scenario.get("scheduled"), today)
        if status in ("planned", "running") and scheduled_age is not None and scheduled_age > 0:
            message = f"scheduled {scheduled_age} days ago and still '{status}'"
            warnings.append(f"scenario {sid}: {message}")
            issues[subject].append(message)
        if status == "failed":
            message = "exercise failed — schedule a retest and record the finding"
            warnings.append(f"scenario {sid}: {message}")
            issues[subject].append(message)

        if status == "passed":
            linked = core.checks_for_scenario(model, sid)
            results = {item.get("kind"): item.get("result") for item in linked}
            for kind in core.CHECK_KINDS:
                if results.get(kind) != "passed":
                    message = f"no passed '{kind}' verification for a completed exercise"
                    errors.append(f"scenario {sid}: {message}")
                    issues[subject].append(message)
            signoff = signoff_index.get(sid)
            if signoff is None or signoff.get("decision") != "approved" or signoff.get("role") != "verifier":
                message = "no approved verifier sign-off for a completed exercise"
                errors.append(f"scenario {sid}: {message}")
                issues[subject].append(message)

    # Communication — who is told, when, and on which channel.
    for stakeholder in stakeholders:
        hid = stakeholder["id"]
        subject = f"stakeholder:{hid}"
        if stakeholder.get("channel") not in channel_index:
            message = f"channel '{stakeholder.get('channel')}' not found"
            errors.append(f"stakeholder {hid}: {message}")
            issues[subject].append(message)

    notified = set()
    for stakeholder in stakeholders:
        notified.update(stakeholder.get("notify", []))
    for moment in core.REQUIRED_NOTIFICATIONS:
        if moment not in notified:
            message = f"no stakeholder is notified at '{moment}' of an exercise"
            warnings.append(message)
            issues["communication:coverage"].append(message)

    cadence = core.parse_duration(plan.get("updates_every"))
    if cadence is None:
        message = f"invalid update cadence '{plan.get('updates_every')}'"
        errors.append("communication plan: " + message)
        issues["communication:plan"].append(message)
    elif cadence > core.MAX_UPDATE_INTERVAL_MS:
        message = (
            f"status updates every {core.format_duration(cadence)} exceed "
            f"{core.format_duration(core.MAX_UPDATE_INTERVAL_MS)}"
        )
        warnings.append("communication plan: " + message)
        issues["communication:plan"].append(message)

    for channel in channels:
        cid = channel["id"]
        if channel.get("audience") in ("external", "both") and not channel.get("approval"):
            message = "external channel without communication approval"
            warnings.append(f"channel {cid}: {message}")
            issues[f"channel:{cid}"].append(message)

    # Verification — evidence and sign-off for service and data recovery.
    for check in checks:
        cid = check["id"]
        subject = f"check:{cid}"
        if check.get("scenario") not in scenario_index:
            message = f"scenario '{check.get('scenario')}' not found"
            errors.append(f"check {cid}: {message}")
            issues[subject].append(message)
        if check.get("result") == "failed":
            message = f"verification failed on '{check.get('metric')}'"
            errors.append(f"check {cid}: {message}")
            issues[subject].append(message)
        if not check.get("evidence"):
            message = "no evidence link"
            warnings.append(f"check {cid}: {message}")
            issues[subject].append(message)

    for signoff in signoffs:
        sid = signoff.get("scenario")
        subject = f"signoff:{sid}"
        if sid not in scenario_index:
            message = f"scenario '{sid}' not found"
            errors.append(f"signoff {sid}: {message}")
            issues[subject].append(message)
            continue
        if signoff.get("person") not in people:
            message = f"participant '{signoff.get('person')}' not found"
            errors.append(f"signoff {sid}: {message}")
            issues[subject].append(message)
        if signoff.get("decision") != "approved":
            message = f"decision is '{signoff.get('decision')}'"
            errors.append(f"signoff {sid}: {message}")
            issues[subject].append(message)
        signed = core.parse_date(signoff.get("date"))
        scheduled = core.parse_date(scenario_index[sid].get("scheduled"))
        if signed is None:
            message = "invalid sign-off date"
            warnings.append(f"signoff {sid}: {message}")
            issues[subject].append(message)
        elif scheduled is not None and signed < scheduled:
            days_before = (scheduled - signed).days
            message = f"signed {days_before} day(s) before the scheduled exercise"
            warnings.append(f"signoff {sid}: {message}")
            issues[subject].append(message)

    return errors, warnings, dict(issues)


def semantic_checks(model: dict, today: date | None = None) -> tuple[list[str], list[str]]:
    errors, warnings, _ = analyse(model, today)
    return errors, warnings


def collect(
    model_dir: str | Path = core.DEFAULT_MODEL,
    schema_dir: str | Path | None = None,
    today: date | None = None,
) -> tuple[dict, list[str], list[str]]:
    """Return (model, errors, warnings)."""
    today = today or date.today()
    model_dir = Path(model_dir)
    errors = schema_errors(model_dir, schema_dir)
    warnings: list[str] = []
    model: dict = {}
    try:
        model = core.load_model(model_dir)
    except (FileNotFoundError, ValueError) as exc:
        errors.append(str(exc))
    if model:
        semantic_errors, warnings = semantic_checks(model, today)
        errors.extend(semantic_errors)
    return model, errors, warnings
