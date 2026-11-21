"""Validation structurelle et sémantique du modèle Fortcloud Custodian."""

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


def _check_duplicates(items: list[dict], label: str, errors: list[str]) -> None:
    counts = Counter(item.get("id") for item in items)
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

    access = model.get("access") or {}
    audit = model.get("audit") or {}
    environments = access.get("environments") or []
    principals = access.get("principals") or []
    grants = access.get("grants") or []
    secrets = model.get("secrets") or []
    pipelines = model.get("changes") or []
    sinks = audit.get("sinks") or []
    operations = audit.get("operations") or []

    for items, label in (
        (environments, "environments"),
        (principals, "principals"),
        (grants, "grants"),
        (secrets, "secrets"),
        (pipelines, "pipelines"),
        (sinks, "sinks"),
        (operations, "operations"),
    ):
        _check_duplicates(items, label, errors)

    envs = core.env_map(model)
    people = core.principal_map(model)
    env_ids = list(envs)

    # Environments and principals — separation of duties.
    for principal in principals:
        pid = principal["id"]
        subject = f"principal:{pid}"
        for environment in principal.get("environments", []):
            if environment not in envs:
                message = f"unknown environment '{environment}'"
                errors.append(f"principal {pid}: {message}")
                issues[subject].append(message)
        if principal.get("type") == "ci" and len(principal.get("environments", [])) > 1:
            message = (
                f"CI principal spans {len(principal['environments'])} environments — "
                "use one identity per environment"
            )
            warnings.append(f"principal {pid}: {message}")
            issues[subject].append(message)

    # Grants — least privilege and environment boundaries.
    for grant in grants:
        gid = grant["id"]
        subject = f"grant:{gid}"
        principal = people.get(grant.get("principal"))
        environment = grant.get("environment")

        if principal is None:
            message = f"principal '{grant.get('principal')}' not found"
            errors.append(f"grant {gid}: {message}")
            issues[subject].append(message)
            continue
        if environment not in envs:
            message = f"unknown environment '{environment}'"
            errors.append(f"grant {gid}: {message}")
            issues[subject].append(message)
            continue
        if environment not in principal.get("environments", []):
            message = f"environment '{environment}' is outside the principal scope"
            errors.append(f"grant {gid}: {message}")
            issues[subject].append(message)

        others = [env for env in env_ids if env != environment]
        for resource in grant.get("resources", []):
            if core.crosses_environment(resource, environment, others):
                message = f"resource '{resource}' targets another environment"
                errors.append(f"grant {gid}: {message}")
                issues[subject].append(message)

        for permission in grant.get("permissions", []):
            if core.is_wildcard(permission):
                message = f"wildcard permission '{permission}' violates least privilege"
                errors.append(f"grant {gid}: {message}")
                issues[subject].append(message)

        if len(grant.get("permissions", [])) > core.MAX_PERMISSIONS:
            message = (
                f"{len(grant['permissions'])} permissions exceed the maximum "
                f"of {core.MAX_PERMISSIONS}"
            )
            warnings.append(f"grant {gid}: {message}")
            issues[subject].append(message)

        expires = core.parse_date(grant.get("expires"))
        if expires is None:
            message = "no expiry date — standing access"
            warnings.append(f"grant {gid}: {message}")
            issues[subject].append(message)
        else:
            remaining = (expires - today).days
            if remaining < 0:
                message = f"expired {-remaining} days ago"
                errors.append(f"grant {gid}: {message}")
                issues[subject].append(message)
            elif remaining > core.MAX_TIME_BOUND_DAYS:
                message = (
                    f"expires in {remaining} days (max {core.MAX_TIME_BOUND_DAYS})"
                )
                warnings.append(f"grant {gid}: {message}")
                issues[subject].append(message)

        if core.is_elevated(grant.get("role")) and expires is None:
            message = f"elevated role '{grant['role']}' without expiry"
            errors.append(f"grant {gid}: {message}")
            issues[subject].append(message)

        if core.is_restricted(model, environment) and not grant.get("approval"):
            message = "restricted environment grant without approval"
            warnings.append(f"grant {gid}: {message}")
            issues[subject].append(message)

    # Secrets — references only, rotation and environment isolation.
    for secret in secrets:
        sid = secret["id"]
        subject = f"secret:{sid}"
        secret_envs = secret.get("environments", [])
        for environment in secret_envs:
            if environment not in envs:
                message = f"unknown environment '{environment}'"
                errors.append(f"secret {sid}: {message}")
                issues[subject].append(message)

        restricted_envs = [env for env in secret_envs if core.is_restricted(model, env)]
        if len(secret_envs) > 1:
            message = f"secret shared across {len(secret_envs)} environments"
            if restricted_envs:
                errors.append(f"secret {sid}: {message}")
                issues[subject].append(message)
            else:
                warnings.append(f"secret {sid}: {message}")
                issues[subject].append(message)

        age = core.secret_age_days(secret, today)
        rotation = int(secret.get("rotation_days", 0) or 0)
        if age is None:
            message = "invalid rotation date"
            errors.append(f"secret {sid}: {message}")
            issues[subject].append(message)
        elif age > rotation:
            message = f"last rotated {age} days ago (policy: {rotation} days)"
            if restricted_envs:
                errors.append(f"secret {sid}: {message}")
                issues[subject].append(message)
            else:
                warnings.append(f"secret {sid}: {message}")
                issues[subject].append(message)

        if rotation > core.MAX_ROTATION_DAYS:
            message = (
                f"rotation policy of {rotation} days exceeds "
                f"{core.MAX_ROTATION_DAYS} days"
            )
            warnings.append(f"secret {sid}: {message}")
            issues[subject].append(message)

        for user in secret.get("used_by", []):
            principal = people.get(user)
            if principal is None:
                message = f"consumer '{user}' not found"
                errors.append(f"secret {sid}: {message}")
                issues[subject].append(message)
            elif not set(principal.get("environments", [])).intersection(secret_envs):
                message = f"consumer '{user}' has no access to the secret environments"
                errors.append(f"secret {sid}: {message}")
                issues[subject].append(message)

        if "k8s-secret" in (secret.get("store"),) and restricted_envs:
            message = "Kubernetes Secret in a restricted environment"
            warnings.append(f"secret {sid}: {message}")
            issues[subject].append(message)

    # Changes — review, tests and rollback before production.
    for pipeline in pipelines:
        pid = pipeline["id"]
        subject = f"pipeline:{pid}"
        environment = pipeline.get("environment")
        if environment not in envs:
            message = f"unknown environment '{environment}'"
            errors.append(f"pipeline {pid}: {message}")
            issues[subject].append(message)
            continue

        restricted = core.is_restricted(model, environment)
        review = pipeline.get("review") or {}
        approvers = int(review.get("approvers", 0) or 0)
        if restricted and not review.get("required"):
            message = "review is not required for a restricted environment"
            errors.append(f"pipeline {pid}: {message}")
            issues[subject].append(message)
        if restricted and approvers < core.MIN_PROD_APPROVERS:
            message = (
                f"{approvers} approver(s) for a restricted environment "
                f"(minimum {core.MIN_PROD_APPROVERS})"
            )
            warnings.append(f"pipeline {pid}: {message}")
            issues[subject].append(message)

        implemented = set(pipeline.get("tests", []))
        missing = [name for name in core.REQUIRED_TESTS if name not in implemented]
        if restricted and missing:
            message = f"missing mandatory test(s): {', '.join(missing)}"
            errors.append(f"pipeline {pid}: {message}")
            issues[subject].append(message)
        if "security" not in implemented:
            message = "no security test in the pipeline"
            warnings.append(f"pipeline {pid}: {message}")
            issues[subject].append(message)

        deployer = people.get(pipeline.get("deployer"))
        if deployer is None:
            message = f"deployer '{pipeline.get('deployer')}' not found"
            errors.append(f"pipeline {pid}: {message}")
            issues[subject].append(message)
        elif environment not in deployer.get("environments", []):
            message = f"deployer '{deployer['id']}' is not scoped to '{environment}'"
            errors.append(f"pipeline {pid}: {message}")
            issues[subject].append(message)

        rollback = pipeline.get("rollback") or {}
        if restricted and not rollback.get("enabled"):
            message = "rollback is not enabled for a restricted environment"
            errors.append(f"pipeline {pid}: {message}")
            issues[subject].append(message)
        if rollback.get("enabled"):
            age = core.rollback_age_days(pipeline, today)
            if age is None:
                message = "rollback has no verified date"
                warnings.append(f"pipeline {pid}: {message}")
                issues[subject].append(message)
            elif age > core.MAX_EVIDENCE_AGE_DAYS:
                message = (
                    f"rollback verification is {age} days old "
                    f"(max {core.MAX_EVIDENCE_AGE_DAYS})"
                )
                warnings.append(f"pipeline {pid}: {message}")
                issues[subject].append(message)
            if restricted and not rollback.get("automate"):
                message = "rollback is not automated for a restricted environment"
                warnings.append(f"pipeline {pid}: {message}")
                issues[subject].append(message)

    # Audit — durable sinks, coverage of sensitive operations and evidence.
    for sink in sinks:
        hid = sink["id"]
        subject = f"sink:{hid}"
        if int(sink.get("retention_days", 0)) < core.MIN_RETENTION_DAYS:
            message = (
                f"retention of {sink['retention_days']} days is below "
                f"{core.MIN_RETENTION_DAYS} days"
            )
            warnings.append(f"sink {hid}: {message}")
            issues[subject].append(message)
        if not sink.get("immutable"):
            message = "log sink is mutable — records can be altered"
            warnings.append(f"sink {hid}: {message}")
            issues[subject].append(message)

    for operation in operations:
        oid = operation["id"]
        subject = f"operation:{oid}"
        environment = operation.get("environment")
        if environment not in envs:
            message = f"unknown environment '{environment}'"
            errors.append(f"operation {oid}: {message}")
            issues[subject].append(message)
        if not operation.get("logged"):
            message = "sensitive operation is not logged"
            errors.append(f"operation {oid}: {message}")
            issues[subject].append(message)
        else:
            sink = core.sink_map(model).get(operation.get("sink"))
            if sink is None:
                message = f"log sink '{operation.get('sink')}' not found"
                errors.append(f"operation {oid}: {message}")
                issues[subject].append(message)

        if not operation.get("evidence"):
            message = "no evidence link"
            warnings.append(f"operation {oid}: {message}")
            issues[subject].append(message)
        else:
            age = core.evidence_age_days(operation, today)
            if age is None:
                message = "no valid evidence date"
                warnings.append(f"operation {oid}: {message}")
                issues[subject].append(message)
            elif age > core.MAX_EVIDENCE_AGE_DAYS:
                message = (
                    f"evidence is {age} days old (max {core.MAX_EVIDENCE_AGE_DAYS})"
                )
                warnings.append(f"operation {oid}: {message}")
                issues[subject].append(message)

        result = operation.get("result")
        if result == "failed":
            message = "audit control failed"
            errors.append(f"operation {oid}: {message}")
            issues[subject].append(message)
        elif result != "passed":
            message = f"result is '{result}'"
            warnings.append(f"operation {oid}: {message}")
            issues[subject].append(message)

    for kind in core.REQUIRED_AUDIT_KINDS:
        if not core.operations_for_kind(model, kind):
            message = f"no audited operation for sensitive kind '{kind}'"
            warnings.append(message)
            issues["audit:coverage"].append(message)

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
