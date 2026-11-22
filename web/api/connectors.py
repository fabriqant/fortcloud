"""Local inventory connector registry and runner.

The browser never receives cloud credentials. It only sends non-secret identifiers
(profile, region, subscription, project). The API then invokes the matching local
connector with the user's ambient CLI configuration and returns the staged proposal.
"""

from __future__ import annotations

import configparser
import importlib.util
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel

WEB_ROOT = Path(__file__).resolve().parents[1]
PROPOSAL_FILE = "components.yaml"
_TIMEOUT_SECONDS = 180
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.@/+:-]{1,128}$")


class ConnectorError(Exception):
    """Raised when a connector cannot be run safely or exits unsuccessfully."""


class ConnectorRun(BaseModel):
    provider: str
    profile: str | None = None
    region: str | None = None
    subscription_id: str | None = None
    project_id: str | None = None


PROVIDERS: dict[str, dict[str, Any]] = {
    "aws": {
        "label": "AWS",
        "description": "EC2 instances, RDS databases and S3 buckets.",
        "module": "connectors.aws",
        "sdk": "boto3",
        "fields": [
            {
                "name": "profile",
                "label": "AWS profile",
                "placeholder": "my-profile",
                "required": False,
                "discovery": "aws_profiles",
                "help": "Leave empty to use the default credential chain.",
            },
            {
                "name": "region",
                "label": "Region",
                "placeholder": "eu-west-3",
                "required": True,
                "default": "eu-west-3",
            },
        ],
    },
    "azure": {
        "label": "Azure",
        "description": "Virtual machines, SQL databases and storage accounts.",
        "module": "connectors.azure",
        "sdk": "azure.identity",
        "fields": [
            {
                "name": "subscription_id",
                "label": "Subscription ID",
                "placeholder": "00000000-0000-0000-0000-000000000000",
                "required": True,
                "discovery": "azure_subscription",
                "help": "Read-only access (Reader role) is enough.",
            }
        ],
    },
    "gcp": {
        "label": "Google Cloud",
        "description": "Compute Engine instances, Cloud SQL and Cloud Storage buckets.",
        "module": "connectors.gcp",
        "sdk": "google.cloud.compute_v1",
        "fields": [
            {
                "name": "project_id",
                "label": "Project ID",
                "placeholder": "my-project",
                "required": True,
                "discovery": "gcp_project",
                "help": "Use a project where you can list resources.",
            }
        ],
    },
}


def _installed(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def _aws_profiles() -> list[str]:
    """Return only profile *names*, never the credential values."""
    names: set[str] = set()
    config = configparser.ConfigParser()
    for filename in (".aws/config", ".aws/credentials"):
        path = Path.home() / filename
        if not path.is_file():
            continue
        config.clear()
        try:
            config.read(path)
        except configparser.Error:
            continue
        for section in config.sections():
            name = section[7:] if section.startswith("profile ") else section
            if name:
                names.add(name)
    return sorted(names)


def _env_value(*names: str) -> list[str]:
    values = [os.environ[name] for name in names if os.environ.get(name)]
    return [value for value in values if _IDENTIFIER.fullmatch(value)]


def _discover(kind: str) -> list[str]:
    if kind == "aws_profiles":
        return _aws_profiles()
    if kind == "azure_subscription":
        return _env_value("AZURE_SUBSCRIPTION_ID")
    if kind == "gcp_project":
        return _env_value("GOOGLE_CLOUD_PROJECT", "GCLOUD_PROJECT")
    return []


def describe(provider: str | None = None) -> list[dict[str, Any]]:
    """Metadata for the connector picker, including discovered non-secret identifiers."""
    if provider and provider not in PROVIDERS:
        raise ConnectorError(f"Unknown connector: {provider}")
    result = []
    for key, spec in PROVIDERS.items():
        if provider and key != provider:
            continue
        fields = []
        for field in spec["fields"]:
            entry = dict(field)
            entry["identifiers"] = _discover(field.get("discovery", "")) if field.get("discovery") else []
            fields.append(entry)
        result.append(
            {
                "id": key,
                "label": spec["label"],
                "description": spec["description"],
                "installed": _installed(spec["sdk"]),
                "fields": fields,
                "proposal": PROPOSAL_FILE,
            }
        )
    return result


def _command(request: ConnectorRun) -> list[str]:
    spec = PROVIDERS[request.provider]
    args = [sys.executable, "-m", spec["module"]]
    for field in spec["fields"]:
        name = field["name"]
        value = getattr(request, name, None)
        if not value:
            continue
        if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
            raise ConnectorError(f"Invalid value for {name}: use letters, digits, . _ - / @ or +")
        args.extend([f"--{name.replace('_', '-')}", value])
    return args


def run(request: ConnectorRun) -> dict[str, Any]:
    """Run one local read-only connector and return its staged proposal status."""
    if request.provider not in PROVIDERS:
        raise ConnectorError(
            "Unknown connector: " + request.provider + ". Expected one of: " + ", ".join(PROVIDERS)
        )
    args = _command(request)
    try:
        completed = subprocess.run(
            args,
            cwd=WEB_ROOT,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ConnectorError(f"Python executable not found: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ConnectorError(f"Connector timed out after {_TIMEOUT_SECONDS}s") from exc

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "connector failed").strip()
        raise ConnectorError(detail[-2000:])

    return {
        "ok": True,
        "provider": request.provider,
        "module": PROVIDERS[request.provider]["module"],
        "command": " ".join(shlex.quote(arg) for arg in args),
        "output": (completed.stdout or "").strip()[-4000:],
        "proposal": PROPOSAL_FILE,
        "imports_dir": str(WEB_ROOT / "workspaces" / "atlas" / "imports"),
    }
