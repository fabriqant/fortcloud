"""Structural and semantic validation of the Fortcloud Ballast model."""

from __future__ import annotations

from collections import Counter, defaultdict
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


def analyse(model: dict) -> tuple[list[str], list[str], dict[str, list[str]]]:
    """Return (errors, warnings, issues keyed by 'flow:<id>' or 'policy:<id>')."""
    errors: list[str] = []
    warnings: list[str] = []
    issues: dict[str, list[str]] = defaultdict(list)

    for key, label in (
        ("services", "services"),
        ("dependencies", "dependencies"),
        ("policies", "policies"),
        ("flows", "flows"),
    ):
        _check_duplicates(model.get(key, []), label, errors)

    services = core.service_map(model)
    dependencies = core.dependency_map(model)
    policies = core.policy_map(model)

    for policy in model.get("policies", []):
        pid = policy["id"]
        subject = f"policy:{pid}"
        dependency = dependencies.get(policy.get("dependency"))
        if dependency is None:
            message = f"dependency '{policy.get('dependency')}' not found"
            errors.append(f"policy {pid}: {message}")
            issues[subject].append(message)
            continue

        retries = policy.get("retries", 0)
        jitter = policy.get("jitter", False)
        multiplier = policy.get("backoff_multiplier", 1)
        reset = core.parse_duration(policy.get("reset_timeout"))

        if retries > 0 and dependency.get("operation") == "write" and not dependency.get("idempotent"):
            message = "retries on a non-idempotent write can duplicate effects"
            errors.append(f"policy {pid}: {message}")
            issues[subject].append(message)

        if dependency.get("criticality") == "P0" and not policy.get("circuit_breaker"):
            message = "no circuit breaker on a P0 dependency"
            errors.append(f"policy {pid}: {message}")
            issues[subject].append(message)

        if retries > 0 and not jitter:
            message = f"retries without jitter (thundering herd risk)"
            warnings.append(f"policy {pid}: {message}")
            issues[subject].append(message)

        if retries > core.MAX_RETRIES:
            message = f"{retries} retries exceed the maximum of {core.MAX_RETRIES}"
            warnings.append(f"policy {pid}: {message}")
            issues[subject].append(message)

        if retries > 0 and multiplier < 2:
            message = f"backoff multiplier {multiplier} is below 2 (insufficient backoff)"
            warnings.append(f"policy {pid}: {message}")
            issues[subject].append(message)

        if not policy.get("bulkhead"):
            message = "no bulkhead isolation for this dependency"
            warnings.append(f"policy {pid}: {message}")
            issues[subject].append(message)

        if dependency.get("criticality") != "P0" and policy.get("fallback") == "none":
            message = (
                f"optional dependency '{dependency['id']}' has no fallback"
            )
            warnings.append(f"policy {pid}: {message}")
            issues[subject].append(message)

        if policy.get("failure_threshold", 0) > core.MAX_FAILURE_THRESHOLD:
            message = (
                f"circuit breaker opens after {policy['failure_threshold']} failures "
                f"(max {core.MAX_FAILURE_THRESHOLD})"
            )
            warnings.append(f"policy {pid}: {message}")
            issues[subject].append(message)

        if reset is None:
            message = "invalid circuit breaker reset_timeout"
            errors.append(f"policy {pid}: {message}")
            issues[subject].append(message)
        elif policy.get("circuit_breaker") and reset > core.MAX_RESET_TIMEOUT_MS:
            message = (
                f"circuit breaker reset_timeout {core.format_duration(reset)} exceeds "
                f"{core.format_duration(core.MAX_RESET_TIMEOUT_MS)}"
            )
            warnings.append(f"policy {pid}: {message}")
            issues[subject].append(message)

    for flow in model.get("flows", []):
        fid = flow["id"]
        subject = f"flow:{fid}"
        service = services.get(flow.get("service"))
        if service is None:
            message = f"service '{flow.get('service')}' not found"
            errors.append(f"flow {fid}: {message}")
            issues[subject].append(message)
            continue

        budget = core.parse_duration(service.get("latency_budget"))
        if budget is None:
            message = f"service '{service['id']}' has an invalid latency_budget"
            errors.append(f"flow {fid}: {message}")
            issues[subject].append(message)
            continue

        total = core.flow_total_ms(model, flow)
        if total > budget:
            message = (
                f"worst case {core.format_duration(total)} exceeds the "
                f"{core.format_duration(budget)} latency budget"
            )
            errors.append(f"flow {fid}: {message}")
            issues[subject].append(message)

        dominant = core.dominant_step(model, flow)
        if dominant:
            step, ratio = dominant
            if ratio > core.DOMINANT_STEP_RATIO:
                message = (
                    f"step '{step.get('dependency')}' consumes {ratio:.0%} of the "
                    "latency budget"
                )
                warnings.append(f"flow {fid}: {message}")
                issues[subject].append(message)

        for index, step in enumerate(flow.get("steps", [])):
            dependency = dependencies.get(step.get("dependency"))
            policy = policies.get(step.get("policy"))
            if dependency is None:
                message = f"step {index}: dependency '{step.get('dependency')}' not found"
                errors.append(f"flow {fid}: {message}")
                issues[subject].append(message)
                continue
            if policy is None:
                message = f"step {index}: policy '{step.get('policy')}' not found"
                errors.append(f"flow {fid}: {message}")
                issues[subject].append(message)
                continue
            if policy.get("dependency") != dependency["id"]:
                message = (
                    f"step {index}: policy '{policy['id']}' targets "
                    f"'{policy.get('dependency')}' but the step uses "
                    f"'{dependency['id']}'"
                )
                errors.append(f"flow {fid}: {message}")
                issues[subject].append(message)

    for dependency in model.get("dependencies", []):
        if not core.flows_using_dependency(model, dependency["id"]):
            message = f"dependency '{dependency['id']}' is not used in any flow"
            warnings.append(message)

    for service in model.get("services", []):
        if not any(flow.get("service") == service["id"] for flow in model.get("flows", [])):
            message = f"service '{service['id']}' has no flow"
            warnings.append(message)

    return errors, warnings, dict(issues)


def semantic_checks(model: dict) -> tuple[list[str], list[str]]:
    errors, warnings, _ = analyse(model)
    return errors, warnings


def collect(
    model_dir: str | Path = core.DEFAULT_MODEL,
    schema_dir: str | Path | None = None,
) -> tuple[dict, list[str], list[str]]:
    """Return (model, errors, warnings)."""
    model_dir = Path(model_dir)
    errors = schema_errors(model_dir, schema_dir)
    warnings: list[str] = []
    model: dict = {}
    try:
        model = core.load_model(model_dir)
    except (FileNotFoundError, ValueError) as exc:
        errors.append(str(exc))
    if model:
        semantic_errors, warnings = semantic_checks(model)
        errors.extend(semantic_errors)
    return model, errors, warnings
