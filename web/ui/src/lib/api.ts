import { getLocale } from "./locale";
import type {
  ArtifactInfo,
  ArtifactPayload,
  Catalog,
  ConnectorInfo,
  ConnectorRunResult,
  ImportDiff,
  ImportInfo,
  Comparison,
  HealthInfo,
  ModelDocument,
  ModelFormat,
  ModelPayload,
  RunResult,
  ScenarioState,
  ToolInfo,
  ViewData,
} from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "Accept-Language": getLocale(),
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = await response.json();
      detail = payload.detail ?? detail;
    } catch {
      // keep the HTTP status text
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthInfo>("/health"),
  tools: () => request<ToolInfo[]>("/tools"),
  catalog: () => request<Catalog>("/catalog"),
  addCatalogValue: (category: string, value: string) =>
    request<{ ok: boolean; added: boolean }>("/catalog", {
      method: "POST",
      body: JSON.stringify({ category, value }),
    }),
  renameCatalogValue: (category: string, value: string, newValue: string) =>
    request<{ ok: boolean; renamed: boolean }>("/catalog", {
      method: "PATCH",
      body: JSON.stringify({ category, value, new_value: newValue }),
    }),
  removeCatalogValue: (category: string, value: string) =>
    request<{ ok: boolean; removed: boolean }>("/catalog", {
      method: "DELETE",
      body: JSON.stringify({ category, value }),
    }),
  model: (tool: string) => request<ModelPayload>(`/${tool}/model`),
  saveFile: (tool: string, file: string, content: string) =>
    request<{ ok: boolean }>(`/${tool}/model/${encodeURIComponent(file)}`, {
      method: "PUT",
      body: JSON.stringify({ content }),
    }),
  reset: (tool: string) => request<ModelPayload>(`/${tool}/model/reset`, { method: "POST" }),
  scenarios: (tool: string) => request<ScenarioState>(`/${tool}/scenarios`),
  createScenario: (tool: string, name: string, description: string) =>
    request<ScenarioState>(`/${tool}/scenarios`, {
      method: "POST",
      body: JSON.stringify({ name, description }),
    }),
  activateScenario: (tool: string, name: string) =>
    request<ScenarioState>(`/${tool}/scenarios/${encodeURIComponent(name)}/activate`, {
      method: "POST",
    }),
  deleteScenario: (tool: string, name: string) =>
    request<ScenarioState>(`/${tool}/scenarios/${encodeURIComponent(name)}`, {
      method: "DELETE",
    }),
  snapshot: (tool: string, label: string) =>
    request<ScenarioState>(`/${tool}/snapshots`, {
      method: "POST",
      body: JSON.stringify({ label }),
    }),
  compare: (tool: string, left: string, right: string) =>
    request<Comparison>(
      `/${tool}/compare?left=${encodeURIComponent(left)}&right=${encodeURIComponent(right)}`,
    ),
  validate: (tool: string, strict: boolean) =>
    request<RunResult>(`/${tool}/validate?strict=${strict}`, { method: "POST" }),
  check: (tool: string, strict: boolean) =>
    request<RunResult>(`/${tool}/check?strict=${strict}`, { method: "POST" }),
  data: (tool: string) => request<ViewData>(`/${tool}/data`),
  artifacts: (tool: string) => request<ArtifactInfo[]>(`/${tool}/artifacts`),
  artifact: (tool: string, name: string) =>
    request<ArtifactPayload>(`/${tool}/artifacts/${encodeURIComponent(name)}`),
  formats: (tool: string) => request<ModelFormat[]>(`/${tool}/formats`),
  document: (tool: string, file: string) =>
    request<ModelDocument>(`/${tool}/model/${encodeURIComponent(file)}/document`),
  saveDocument: (tool: string, file: string, document: Record<string, unknown>) =>
    request<{ ok: boolean }>(`/${tool}/model/${encodeURIComponent(file)}/document`, {
      method: "PUT",
      body: JSON.stringify({ document }),
    }),
  schemas: (tool: string) => request<Record<string, string>>(`/${tool}/schemas`),
  imports: (tool: string) => request<ImportInfo[]>(`/${tool}/imports`),
  stageImport: (tool: string, file: string, content: string) =>
    request<{ ok: boolean }>(`/${tool}/imports`, {
      method: "POST",
      body: JSON.stringify({ file, content }),
    }),
  importDiff: (tool: string, file: string) =>
    request<ImportDiff>(`/${tool}/imports/${encodeURIComponent(file)}/diff`),
  acceptImport: (tool: string, file: string) =>
    request<{ ok: boolean }>(`/${tool}/imports/${encodeURIComponent(file)}/accept`, {
      method: "POST",
    }),
  discardImport: (tool: string, file: string) =>
    request<{ ok: boolean }>(`/${tool}/imports/${encodeURIComponent(file)}`, {
      method: "DELETE",
    }),
  connectors: () => request<ConnectorInfo[]>("/connectors"),
  runConnector: (payload: Record<string, string>) =>
    request<ConnectorRunResult>("/connectors/run", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
