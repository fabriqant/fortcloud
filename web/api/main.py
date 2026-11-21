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

from . import registry, runner, structured, workspaces

app = FastAPI(
    title="Fortcloud Console API",
    version="0.1.0",
    description="Local API for the seven standalone Fortcloud resilience tools.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Content-Type"],
)


class ModelFile(BaseModel):
    content: str


class InventoryRequest(BaseModel):
    source: str = "terraform"
    profile: str | None = None


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
    """Reserved for the optional AWS/IaC inventory importer (next iteration)."""
    return {
        "available": False,
        "source": request.source,
        "message": (
            "Inventory import is not part of this prototype. The importer will propose YAML "
            "for review before any model file is written."
        ),
    }


_UI_DIST = Path(__file__).resolve().parents[1] / "ui" / "dist"
if _UI_DIST.is_dir():
    app.mount("/", StaticFiles(directory=_UI_DIST, html=True), name="ui")
