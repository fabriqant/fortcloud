export type Catalog = Record<string, string[]>;

export interface ArtifactInfo {
  name: string;
  label: string;
  kind: "markdown" | "mermaid" | "json";
  available: boolean;
  size: number;
}

export interface ToolInfo {
  id: string;
  name: string;
  tagline: string;
  description: string;
  accent: string;
  icon: string;
  artifacts: ArtifactInfo[];
}

export interface RunResult {
  tool: string;
  ok: boolean;
  exit_code: number;
  errors: string[];
  warnings: string[];
  strict: boolean;
  artifacts?: ArtifactInfo[];
}

export interface Kpi {
  key: string;
  label: string;
  value: number;
  tone: "danger" | "warning" | "neutral";
}

export interface ChartSeries {
  id: string;
  label: string;
  type: "bar" | "donut";
  data: { name: string; value: number }[];
}

export interface DataTableInfo {
  id: string;
  label: string;
  columns: { key: string; label: string }[];
  rows: Record<string, string>[];
  total: number;
}

export interface ViewData {
  tool: string;
  summary: Record<string, number>;
  kpis: Kpi[];
  charts: ChartSeries[];
  tables: DataTableInfo[];
  graph: string;
  errors: string[];
  warnings: string[];
}

export interface ModelPayload {
  tool: string;
  model_dir: string;
  files: Record<string, string>;
}

export interface ArtifactPayload {
  tool: string;
  name: string;
  content: string;
}

export interface ModelFormat {
  file: string;
  schema: string;
}

export interface ModelDocument {
  tool: string;
  file: string;
  document: Record<string, unknown>;
}

export interface SnapshotInfo {
  version: number;
  label: string;
  created_at: string;
}

export interface ScenarioInfo {
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  active: boolean;
  versions: SnapshotInfo[];
}

export interface ScenarioState {
  active: string;
  scenarios: ScenarioInfo[];
}

export interface ComparisonFile {
  file: string;
  changed: boolean;
  diff: string;
}

export interface Comparison {
  left: string;
  right: string;
  files: ComparisonFile[];
}

export interface ImportInfo {
  name: string;
  size: number;
}

export interface ImportDiff {
  file: string;
  changed: boolean;
  current: string;
  proposed: string;
  diff: string;
}

export interface ConnectorField {
  name: string;
  label: string;
  placeholder: string;
  required: boolean;
  default?: string;
  help?: string;
  identifiers: string[];
}

export interface ConnectorInfo {
  id: string;
  label: string;
  description: string;
  installed: boolean;
  fields: ConnectorField[];
  proposal: string;
}

export interface ConnectorRunResult {
  ok: boolean;
  provider: string;
  module: string;
  command: string;
  output: string;
  proposal: string;
  imports_dir: string;
}

export type TabKey = "overview" | "model" | "outputs" | "scenarios" | "import" | "schemas";
