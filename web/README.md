# Fortcloud Console (web prototype)

A single, calm interface for the seven standalone Fortcloud tools. It is a **consumer** of the tools, not an eighth tool: the CLIs, packages, schemas and examples stay untouched.

The console imports the Python packages directly in-process. It does not spawn CLIs, does not call AWS, and does not change the tools' bundled example models.

## What works in this prototype

- Seven-tool sidebar driven by [`api/tools.yaml`](api/tools.yaml).
- One file-backed workspace per tool under `web/workspaces/<tool>/`.
- YAML model editor with line numbers, dirty state and explicit save.
- `Validate`, `Check`, `Strict` and reset-to-example actions.
- KPI cards, Mermaid dependency graph, Recharts charts and sortable/filterable TanStack tables.
- Generated Markdown, Mermaid and JSON artifacts rendered read-only, with download.
- JSON Schemas served to the browser and displayed in a dedicated tab.
- Error and warning panel with the exact diagnostics returned by the tool.
- API tests and a production UI build in CI.

Not included yet: AWS/IaC inventory import (the endpoint is reserved), Monaco-based YAML completion, authentication and multi-user hosting.

## Architecture

```text
Browser (React + Vite)
  │  JSON over HTTP
  ▼
FastAPI (web/api)
  │  imports fortcloud_atlas, fortcloud_failover, ... directly
  ▼
web/workspaces/<tool>/model/*.yaml     <- editable source of truth
web/workspaces/<tool>/artifacts/*      <- generated, disposable
```

Everything stays local by default. The API binds to `127.0.0.1` when started with the command below.

## Quick start

From the repository root:

```bash
python -m pip install -r web/requirements.txt
python -m pytest web/tests -q
```

Terminal 1 — API:

```bash
python -m uvicorn api.main:app --app-dir web --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — UI:

```bash
cd web/ui
npm install
npm run dev
```

Open <http://127.0.0.1:5173>.

For a single-process setup, build the UI (`cd web/ui && npm run build`) and start the API. It serves `web/ui/dist` automatically at <http://127.0.0.1:8000>.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Service status |
| `GET` | `/api/tools` | Registry of the seven tools |
| `GET` | `/api/{tool}/model` | YAML files of the workspace |
| `PUT` | `/api/{tool}/model/{file}` | Save one YAML file |
| `POST` | `/api/{tool}/model/reset` | Restore the bundled example |
| `POST` | `/api/{tool}/validate?strict=` | Errors and warnings only |
| `POST` | `/api/{tool}/check?strict=` | Validate, regenerate artifacts, return status |
| `GET` | `/api/{tool}/data` | KPIs, charts, tables and Mermaid source |
| `GET` | `/api/{tool}/artifacts` | Artifact list |
| `GET` | `/api/{tool}/artifacts/{name}` | Artifact content |
| `GET` | `/api/{tool}/schemas` | JSON Schemas |

`{tool}` is one of `atlas`, `failover`, `ark`, `ballast`, `vitals`, `custodian`, `crucible`.

Exit codes follow the CLI contract: `0` for success, `1` for validation failures, including warnings in strict mode.

## Files

```text
web/
├── api/
│   ├── main.py           FastAPI app and routes
│   ├── registry.py       tools.yaml loader and tool paths
│   ├── tools.yaml        single source of truth for the UI shell
│   ├── workspaces.py     file storage and example seeding
│   ├── runner.py         imports the tool packages and runs check()
│   └── structured.py     view models for KPIs, charts and tables
├── ui/
│   ├── src/App.tsx       layout, actions and state
│   └── src/components/   sidebar, cards, graph, tables, editor, outputs
├── tests/test_api.py     API smoke tests
├── requirements.txt      API and editable tool installs
└── README.md             this file
```

Generated workspaces are ignored by Git. Delete `web/workspaces/` at any time: the next request recreates it from the examples.
