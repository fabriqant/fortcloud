"""Local API for the FortCloud web console.

The API imports the seven tool packages directly. It never shells out to the tool
CLIs and never modifies the tools' own example models. On explicit request it can
run one of the local read-only inventory connectors; no cloud credentials are sent
to the browser or stored by the API.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import catalog, connectors, i18n, registry, runner, snapshots, structured, workspaces

SUITE_VERSION = "0.1.0"

app = FastAPI(
    title="FortCloud Console API",
    version=SUITE_VERSION,
    description="Local API for the seven standalone FortCloud resilience tools.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(HTTPException)
async def translated_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    detail = i18n.translate_error(i18n.language_from_request(request), exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
        headers=exc.headers,
    )


class ModelFile(BaseModel):
    content: str


class ImportFile(BaseModel):
    file: str
    content: str


class DocumentPayload(BaseModel):
    document: dict


class InventoryRequest(BaseModel):
    source: str = "terraform"
    profile: str | None = None


class CatalogValue(BaseModel):
    category: str
    value: str


class CatalogRename(CatalogValue):
    new_value: str


class ScenarioRequest(BaseModel):
    name: str
    description: str = ""


class SnapshotRequest(BaseModel):
    label: str = ""


def _tool(tool_id: str) -> registry.Tool:
    try:
        return registry.get_tool(tool_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _localized_artifacts(tool_id: str, language: str, records: list[dict]) -> list[dict]:
    labels = {
        artifact.name: artifact.label
        for artifact in registry.get_tool(tool_id, language).artifacts
    }
    for record in records:
        label = labels.get(record.get("name"))
        if label:
            record["label"] = label
    return records


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "tools": len(registry.load_tools()), "version": SUITE_VERSION}


@app.get("/api/tools")
def tools(request: Request) -> list[dict]:
    return registry.public_tools(i18n.language_from_request(request))


@app.get("/api/catalog")
def get_catalog() -> dict[str, list[str]]:
    """Reusable reference values offered as suggestions in guided forms."""
    return catalog.list_values()


@app.post("/api/catalog")
def add_catalog_value(payload: CatalogValue) -> dict:
    try:
        added = catalog.add_value(payload.category, payload.value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "added": added}


@app.patch("/api/catalog")
def rename_catalog_value(payload: CatalogRename) -> dict:
    try:
        renamed = catalog.rename_value(payload.category, payload.value, payload.new_value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "renamed": renamed}


@app.delete("/api/catalog")
def remove_catalog_value(payload: CatalogValue) -> dict:
    try:
        removed = catalog.remove_value(payload.category, payload.value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "removed": removed}


@app.get("/api/{tool_id}/model")
def get_model(tool_id: str) -> dict:
    tool = _tool(tool_id)
    return {
        "tool": tool.id,
        "model_dir": str(tool.model_dir),
        "files": workspaces.read_model(tool),
    }


@app.put("/api/{tool_id}/model/{filename}")
def put_model_file(tool_id: str, filename: str, payload: ModelFile) -> dict:
    tool = _tool(tool_id)
    try:
        workspaces.write_model_file(tool, filename, payload.content)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "tool": tool.id, "file": filename}


@app.post("/api/{tool_id}/model/reset")
def reset_model(tool_id: str) -> dict:
    tool = _tool(tool_id)
    snapshots.activate_scenario(tool, snapshots.DEFAULT_SCENARIO)
    return {"ok": True, "tool": tool.id, "files": workspaces.read_model(tool)}


@app.get("/api/{tool_id}/scenarios")
def list_scenarios(tool_id: str, request: Request) -> dict:
    language = i18n.language_from_request(request)
    result = snapshots.list_scenarios(_tool(tool_id))
    descriptions = i18n.resource(language, "scenarios.json").get("descriptions", {})
    if not isinstance(descriptions, dict):
        return result
    for scenario in result.get("scenarios", []):
        if isinstance(scenario, dict) and scenario.get("name") in descriptions:
            scenario["description"] = str(descriptions[scenario["name"]])
    return result


@app.post("/api/{tool_id}/scenarios")
def create_scenario(tool_id: str, payload: ScenarioRequest) -> dict:
    try:
        return snapshots.create_scenario(
            _tool(tool_id), payload.name, payload.description
        )
    except snapshots.SnapshotError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/{tool_id}/scenarios/{name}/activate")
def activate_scenario(tool_id: str, name: str) -> dict:
    try:
        return snapshots.activate_scenario(_tool(tool_id), name)
    except snapshots.SnapshotError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.delete("/api/{tool_id}/scenarios/{name}")
def delete_scenario(tool_id: str, name: str) -> dict:
    try:
        return snapshots.delete_scenario(_tool(tool_id), name)
    except snapshots.SnapshotError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/{tool_id}/snapshots")
def create_snapshot(tool_id: str, payload: SnapshotRequest) -> dict:
    return snapshots.snapshot(_tool(tool_id), payload.label)


@app.get("/api/{tool_id}/compare")
def compare_models(tool_id: str, left: str, right: str) -> dict:
    try:
        return snapshots.compare(_tool(tool_id), left, right)
    except snapshots.SnapshotError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/{tool_id}/imports")
def list_imports(tool_id: str) -> list[dict]:
    tool = _tool(tool_id)
    workspaces.ensure_workspace(tool)
    path = workspaces.import_dir(tool)
    return [
        {
            "name": name,
            "size": (path / name).stat().st_size,
        }
        for name in workspaces.import_files(tool)
    ]


@app.post("/api/{tool_id}/imports")
def stage_import(tool_id: str, payload: ImportFile) -> dict:
    tool = _tool(tool_id)
    try:
        workspaces.stage_import(tool, payload.file, payload.content)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "tool": tool.id, "file": payload.file}


@app.get("/api/{tool_id}/imports/{filename}/diff")
def get_import_diff(tool_id: str, filename: str) -> dict:
    tool = _tool(tool_id)
    try:
        return workspaces.import_diff(tool, filename)
    except (KeyError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/{tool_id}/imports/{filename}/accept")
def accept_import(tool_id: str, filename: str) -> dict:
    tool = _tool(tool_id)
    try:
        files = workspaces.accept_import(tool, filename)
    except (KeyError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "tool": tool.id, "files": files}


@app.delete("/api/{tool_id}/imports/{filename}")
def delete_import(tool_id: str, filename: str) -> dict:
    tool = _tool(tool_id)
    try:
        workspaces.discard_import(tool, filename)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "tool": tool.id, "file": filename}


@app.post("/api/{tool_id}/validate")
def validate_model(tool_id: str, request: Request, strict: bool = False) -> dict:
    language = i18n.language_from_request(request)
    result = runner.validate(_tool(tool_id), strict=strict)
    result.pop("model", None)
    result["errors"] = i18n.translate_messages(language, result["errors"])
    result["warnings"] = i18n.translate_messages(language, result["warnings"])
    return result


@app.post("/api/{tool_id}/check")
def check_model(tool_id: str, request: Request, strict: bool = False) -> dict:
    language = i18n.language_from_request(request)
    result = runner.check(_tool(tool_id), strict=strict)
    result["errors"] = i18n.translate_messages(language, result["errors"])
    result["warnings"] = i18n.translate_messages(language, result["warnings"])
    result["artifacts"] = _localized_artifacts(tool_id, language, result["artifacts"])
    return result


@app.get("/api/{tool_id}/artifacts")
def list_artifacts(tool_id: str, request: Request) -> list[dict]:
    tool = _tool(tool_id)
    workspaces.ensure_workspace(tool)
    language = i18n.language_from_request(request)
    return _localized_artifacts(tool_id, language, workspaces.artifact_records(tool))


@app.get("/api/{tool_id}/artifacts/{name}")
def get_artifact(tool_id: str, name: str, request: Request) -> dict:
    tool = _tool(tool_id)
    try:
        content = workspaces.read_artifact(tool, name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Artifact not generated: {name}") from exc
    language = i18n.language_from_request(request)
    return {
        "tool": tool.id,
        "name": name,
        "content": i18n.translate_artifact(language, name, content),
    }


@app.get("/api/{tool_id}/data")
def get_data(tool_id: str, request: Request) -> dict:
    tool = _tool(tool_id)
    model, errors, warnings = runner.collect(tool)
    language = i18n.language_from_request(request)
    result = structured.build(tool, model, language)
    result.update(
        {
            "tool": tool.id,
            "errors": i18n.translate_messages(language, errors),
            "warnings": i18n.translate_messages(language, warnings),
        }
    )
    return result


@app.get("/api/{tool_id}/formats")
def list_formats(tool_id: str) -> list[dict]:
    tool = _tool(tool_id)
    core, _, _ = runner.load_modules(tool)
    return [
        {"file": filename, "schema": schema_filename}
        for filename, schema_filename in core.FILES.values()
    ]


@app.get("/api/{tool_id}/model/{filename}/document")
def get_document(tool_id: str, filename: str) -> dict:
    tool = _tool(tool_id)
    try:
        document = workspaces.read_model_document(tool, filename)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"tool": tool.id, "file": filename, "document": document}


@app.put("/api/{tool_id}/model/{filename}/document")
def put_document(tool_id: str, filename: str, payload: DocumentPayload) -> dict:
    tool = _tool(tool_id)
    try:
        workspaces.write_model_document(tool, filename, payload.document)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"ok": True, "tool": tool.id, "file": filename}


@app.get("/api/{tool_id}/schemas")
def list_schemas(tool_id: str, request: Request) -> dict[str, str]:
    tool = _tool(tool_id)
    core, _, _ = runner.load_modules(tool)
    language = i18n.language_from_request(request)
    schemas = {}
    for _, schema_filename in core.FILES.values():
        path = tool.schema_dir / schema_filename
        if path.is_file():
            schemas[schema_filename] = i18n.translate_schema(
                tool_id,
                schema_filename,
                path.read_text(encoding="utf-8"),
                language,
            )
    return schemas


@app.get("/api/connectors")
def list_connectors(request: Request) -> list[dict]:
    """Connector metadata and discovered, non-secret identifiers."""
    return connectors.describe(language=i18n.language_from_request(request))


@app.post("/api/connectors/run")
def run_connector(request: connectors.ConnectorRun) -> dict:
    """Run a local read-only connector; the browser sends identifiers only."""
    try:
        return connectors.run(request)
    except connectors.ConnectorError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/atlas/inventory")
def propose_inventory(request: InventoryRequest, http_request: Request) -> dict:
    """Describe the local connectors; the console itself never reads a cloud account."""
    tool = registry.get_tool("atlas")
    language = i18n.language_from_request(http_request)
    source = request.source or "aws"
    known = {"aws", "azure", "gcp"}
    command = (
        f"python -m connectors.{source}"
        if source in known
        else "python -m connectors.aws --profile <profile> --region <region>"
    )
    message = i18n.resource(language, "api.json").get(
        "inventory_message",
        "The console does not connect to clouds directly. Run a local read-only connector "
        "where your cloud CLI is configured. It writes a proposal to the imports folder; "
        "review it in the Import tab before accepting it.",
    )
    return {
        "direct_access": False,
        "source": source,
        "connector": command,
        "providers": connectors.describe(language=language),
        "imports_dir": str(tool.workspace_dir / "imports"),
        "message": str(message),
    }


_UI_DIST = Path(__file__).resolve().parents[1] / "ui" / "dist"
if _UI_DIST.is_dir():
    app.mount("/", StaticFiles(directory=_UI_DIST, html=True), name="ui")
