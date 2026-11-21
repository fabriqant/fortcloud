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

export type TabKey = "overview" | "model" | "outputs" | "import" | "schemas";
