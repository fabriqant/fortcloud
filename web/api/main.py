"""Local API for the Fortcloud web console.

The API imports the seven tool packages directly. It never shells out to the CLIs
and never modifies the tools' own example models.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import catalog, registry, runner, snapshots, structured, workspaces

app = FastAPI(
    title="Fortcloud Console API",
    version="0.1.0",
    description="Local API for the seven standalone Fortcloud resilience tools.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
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


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "tools": len(registry.load_tools())}


@app.get("/api/tools")
def tools() -> list[dict]:
    return [registry.public_tool(tool) for tool in registry.load_tools()]


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
    workspaces.reset_model(tool)
    return {"ok": True, "tool": tool.id, "files": workspaces.read_model(tool)}


@app.get("/api/{tool_id}/scenarios")
def list_scenarios(tool_id: str) -> dict:
    return snapshots.list_scenarios(_tool(tool_id))


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
def validate_model(tool_id: str, strict: bool = False) -> dict:
    result = runner.validate(_tool(tool_id), strict=strict)
    result.pop("model", None)
    return result


@app.post("/api/{tool_id}/check")
def check_model(tool_id: str, strict: bool = False) -> dict:
    return runner.check(_tool(tool_id), strict=strict)


@app.get("/api/{tool_id}/artifacts")
def list_artifacts(tool_id: str) -> list[dict]:
    tool = _tool(tool_id)
    workspaces.ensure_workspace(tool)
    return workspaces.artifact_records(tool)


@app.get("/api/{tool_id}/artifacts/{name}")
def get_artifact(tool_id: str, name: str) -> dict:
    tool = _tool(tool_id)
    try:
        content = workspaces.read_artifact(tool, name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Artifact not generated: {name}") from exc
    return {"tool": tool.id, "name": name, "content": content}


@app.get("/api/{tool_id}/data")
def get_data(tool_id: str) -> dict:
    tool = _tool(tool_id)
    model, errors, warnings = runner.collect(tool)
    result = structured.build(tool, model)
    result.update({"tool": tool.id, "errors": errors, "warnings": warnings})
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
def list_schemas(tool_id: str) -> dict[str, str]:
    tool = _tool(tool_id)
    core, _, _ = runner.load_modules(tool)
    schemas = {}
    for _, schema_filename in core.FILES.values():
        path = tool.schema_dir / schema_filename
        if path.is_file():
            schemas[schema_filename] = path.read_text(encoding="utf-8")
    return schemas


@app.post("/api/atlas/inventory")
def propose_inventory(request: InventoryRequest) -> dict:
    """Describe the local connector; the console itself never reads a cloud account."""
    tool = registry.get_tool("atlas")
    return {
        "direct_access": False,
        "source": request.source,
        "connector": "python -m connectors.aws --profile <profile> --region <region>",
        "imports_dir": str(tool.workspace_dir / "imports"),
        "message": (
            "The console does not connect to clouds. Run the local read-only connector where "
            "your AWS profile is configured. It writes a proposal to the imports folder; review "
            "it in the Import tab before accepting it."
        ),
    }


_UI_DIST = Path(__file__).resolve().parents[1] / "ui" / "dist"
if _UI_DIST.is_dir():
    app.mount("/", StaticFiles(directory=_UI_DIST, html=True), name="ui")
