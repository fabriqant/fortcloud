# Fortcloud Console (web prototype)

A single, calm interface for the seven standalone Fortcloud tools. It is a **consumer** of the tools, not an eighth tool: the CLIs, packages, schemas and examples stay untouched.

The API imports the Python packages directly in-process. It does not spawn CLIs and does not change the tools' bundled example models. The optional AWS connector runs as a separate local command with your own AWS profile; the API and browser never handle credentials.

## What works in this prototype

- Seven-tool sidebar driven by [`api/tools.yaml`](api/tools.yaml).
- One file-backed workspace per tool under `web/workspaces/<tool>/`.
- Guided forms generated from each tool's JSON Schema: catalog-backed fields use the same select style as schema enums, with a custom-value fallback; arrays are compact accordion lists instead of nested cards. A local SQLite reference catalog seeds owners, teams, regions, zones, providers, roles, pairs, components, scenarios, risks, checks and more, and can be edited in a modal; the YAML source editor stays available with line numbers, dirty state and explicit save.
- Named scenarios per tool with independent model copies, automatic version snapshots on every save, manual labelled snapshots and a Scenarios tab (before Model) that compares any two versions with a unified diff. The Overview tab has a scenario selector: KPIs, charts, tables and outputs follow the chosen scenario; switching back restores its latest version exactly.
- Staged YAML import: paste or upload a proposal, review a unified diff, then accept or discard it. Nothing is applied automatically.
- `Validate`, `Check`, `Strict` and reset-to-example actions.
- KPI cards, Mermaid dependency graph, Recharts charts and sortable/filterable TanStack tables.
- Generated Markdown, Mermaid and JSON artifacts rendered read-only, with download.
- JSON Schemas served to the browser and displayed in a dedicated tab.
- Error and warning panel with the exact diagnostics returned by the tool.
- Optional local read-only AWS connector that writes an Atlas proposal for review.
- API and connector tests plus a production UI build in CI.

Not included: direct cloud access from the browser or API, Monaco-based YAML completion, authentication and multi-user hosting.

## Architecture

```text
Browser (React + Vite)
  │  JSON over HTTP
  ▼
FastAPI (web/api)
  │  imports fortcloud_atlas, fortcloud_failover, ... directly
  ▼
web/workspaces/<tool>/model/*.yaml         <- editable source of truth
web/workspaces/<tool>/artifacts/*          <- generated, disposable
web/workspaces/<tool>/imports/*            <- staged proposals, never auto-applied
web/workspaces/<tool>/scenarios/<name>/    <- version snapshots per scenario
web/catalog.sqlite3                        <- reusable reference values for guided forms
```

Optional, outside the API:

```text
Local AWS profile -> python -m connectors.aws -> web/workspaces/atlas/imports/components.yaml
                          (read-only APIs)              |  reviewed in the Import tab
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

## Local AWS connector (optional)

The connector is a standalone command, not part of the API. Install its dependency only if you need it:

```bash
python -m pip install -r web/connectors/requirements-aws.txt
python -m connectors.aws --profile my-profile --region eu-west-3 --dry-run
python -m connectors.aws --profile my-profile --region eu-west-3
```

It uses the standard `boto3` credential chain from your local AWS configuration, calls only read-only APIs (`ec2:DescribeInstances`, `rds:DescribeDBInstances`, `s3:ListBuckets`), and writes `web/workspaces/atlas/imports/components.yaml`. It never writes to `model/`. Use `--out` for another destination. Open the **Import** tab, review the diff, then accept or discard the proposal. Run `Validate` before `Check` as usual.

No credentials are sent to the console, stored in a workspace, or written to a proposal. Without `boto3`, the API, UI and all other tools work unchanged.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/health` | Service status |
| `GET` | `/api/tools` | Registry of the seven tools |
| `GET` | `/api/catalog` | Reference values grouped by category |
| `POST` | `/api/catalog` | Add a reference value |
| `PATCH` | `/api/catalog` | Rename a reference value |
| `DELETE` | `/api/catalog` | Remove a reference value |
| `GET` | `/api/{tool}/model` | YAML files of the workspace |
| `PUT` | `/api/{tool}/model/{file}` | Save one YAML file |
| `GET` | `/api/{tool}/formats` | Model file → JSON Schema map |
| `GET` | `/api/{tool}/model/{file}/document` | Read a model as structured data |
| `PUT` | `/api/{tool}/model/{file}/document` | Save structured model data as YAML |
| `POST` | `/api/{tool}/model/reset` | Restore the bundled example |
| `GET` | `/api/{tool}/scenarios` | Scenarios, versions and the active name |
| `POST` | `/api/{tool}/scenarios` | Create a named scenario from the current model |
| `POST` | `/api/{tool}/scenarios/{name}/activate` | Restore a scenario's latest version |
| `DELETE` | `/api/{tool}/scenarios/{name}` | Delete a scenario (`base` is protected) |
| `POST` | `/api/{tool}/snapshots` | Record the current model as a new version |
| `GET` | `/api/{tool}/compare?left=&right=` | Unified diff of two versions or the live model |
| `GET` | `/api/{tool}/imports` | List staged proposals |
| `POST` | `/api/{tool}/imports` | Stage a YAML proposal |
| `GET` | `/api/{tool}/imports/{file}/diff` | Unified diff against the current model |
| `POST` | `/api/{tool}/imports/{file}/accept` | Replace a model file with the proposal |
| `DELETE` | `/api/{tool}/imports/{file}` | Discard a proposal |
| `POST` | `/api/{tool}/validate?strict=` | Errors and warnings only |
| `POST` | `/api/{tool}/check?strict=` | Validate, regenerate artifacts, return status |
| `GET` | `/api/{tool}/data` | KPIs, charts, tables and Mermaid source |
| `GET` | `/api/{tool}/artifacts` | Artifact list |
| `GET` | `/api/{tool}/artifacts/{name}` | Artifact content |
| `GET` | `/api/{tool}/schemas` | JSON Schemas |
| `POST` | `/api/atlas/inventory` | Connector instructions; no cloud access |

`{tool}` is one of `atlas`, `failover`, `ark`, `ballast`, `vitals`, `custodian`, `crucible`.

Exit codes follow the CLI contract: `0` for success, `1` for validation failures, including warnings in strict mode.

## Files

```text
web/
├── api/
│   ├── main.py           FastAPI app and routes
│   ├── catalog.py        local SQLite reference-value catalog
│   ├── registry.py       tools.yaml loader and tool paths
│   ├── tools.yaml        single source of truth for the UI shell
│   ├── workspaces.py     file storage and example seeding
│   ├── snapshots.py      named scenarios, versions and comparison
│   ├── runner.py         imports the tool packages and runs check()
│   └── structured.py     view models for KPIs, charts and tables
├── ui/
│   ├── src/App.tsx       layout, actions and state
│   └── src/components/   sidebar, forms, cards, graph, tables, editor, outputs
├── connectors/
│   ├── aws/
│   │   ├── collector.py  read-only AWS to Atlas component mapping
│   │   └── __main__.py   local CLI entry point
│   └── requirements-aws.txt   optional boto3 dependency
├── tests/
│   ├── test_api.py       API and import smoke tests
│   ├── test_catalog.py   reference catalog CRUD tests
│   ├── test_snapshots.py scenario, snapshot and comparison tests
│   └── test_aws_connector.py  connector mapping with a fake session
├── requirements.txt      API and editable tool installs
└── README.md             this file
```

Generated workspaces and the local reference catalog are ignored by Git. Delete `web/workspaces/` at any time: the next request recreates the model from the examples, and all scenarios, snapshots and staged proposals disappear with it. Delete `web/catalog.sqlite3` to restore the default reference values; edits made in the Reference data modal are otherwise kept locally.
