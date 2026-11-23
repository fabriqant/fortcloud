# French display translations

These files are **display-only translation resources** for the FortCloud console. They translate labels, taglines, descriptions, help text and prose shown to the user; they do not change any data or behaviour.

- Raw identifiers, file names, JSON/YAML keys, enum raw values, cloud provider names and technical values (`P0`, `eu-west-1`, `SLO`, `RTO`, `FMEA`, `check`, …) must stay unchanged.
- Only display strings are translated. Do not add entries for technical overrides such as placeholders, defaults, SDK/module names or discovery keys.
- English remains the source language and the fallback: any key missing from these files falls back to the English value from `web/api/tools.yaml`, `web/api/connectors.py`, `web/api/structured.py` and the `*/schema/*.json` files.

Files:

- `tools.yaml` — tool taglines, descriptions and artifact labels (keyed by tool id, then artifact file name).
- `connectors.json` — provider descriptions and field labels/help (keyed by provider id and field name).
- `structured.json` — KPI/column labels, chart and table titles, boolean values and component categories.
- `schemas.json` — schema `title` values (keyed by the exact English title, including punctuation).
- `scenarios.json` — descriptions of the three tracked starter scenarios (custom scenario descriptions stay as authored).
- `api.json` — short API-generated guidance shown by the console.
- `diagnostics.json` — validator findings and common JSON Schema messages.
- `api_errors.json` — API error details such as missing artifacts and unknown tools.
- `artifacts.json` — generated Markdown/Mermaid headings, table labels and prose.

`diagnostics.json`, `api_errors.json` and `artifacts.json` use an `exact` map (whole messages or whole lines) plus an ordered `patterns` list. The API applies them at response time; canonical Markdown files on disk stay in English.
