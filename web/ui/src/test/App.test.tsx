import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import i18n from "../i18n";
import type { ToolInfo } from "../lib/types";

const mocks = vi.hoisted(() => ({
  tools: vi.fn(),
  health: vi.fn(),
  catalog: vi.fn(),
  model: vi.fn(),
  data: vi.fn(),
  artifacts: vi.fn(),
  schemas: vi.fn(),
  scenarios: vi.fn(),
  artifact: vi.fn(),
  imports: vi.fn(),
  importDiff: vi.fn(),
}));

vi.mock("../lib/api", () => ({ api: mocks }));
vi.mock("../components/FormView", () => ({ FormView: () => null }));
vi.mock("../components/GraphView", () => ({ GraphView: () => null }));
vi.mock("../components/ChartCard", () => ({ ChartCard: () => null }));
vi.mock("../components/DataTable", () => ({ DataTable: () => null }));
vi.mock("../components/ModelEditor", () => ({ ModelEditor: () => null }));
vi.mock("../components/ScenarioView", () => ({ ScenarioView: () => null }));
vi.mock("../components/ArtifactView", () => ({ ArtifactView: () => null }));
vi.mock("../components/ImportView", () => ({ ImportView: () => null }));

const tools: ToolInfo[] = [
  ["atlas", "Atlas"],
  ["failover", "Failover"],
  ["ark", "Ark"],
  ["ballast", "Ballast"],
  ["vitals", "Vitals"],
  ["custodian", "Custodian"],
  ["crucible", "Crucible"],
].map(([id, name]) => ({
  id,
  name: `FortCloud ${name}`,
  tagline: `${name} tagline`,
  description: `${name} description`,
  accent: "blue",
  icon: "activity",
  artifacts: [],
}));

describe("App routing and localized tabs", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    vi.resetAllMocks();

    mocks.tools.mockResolvedValue(tools);
    mocks.health.mockResolvedValue({ status: "ok", tools: 7, version: "0.1.0" });
    mocks.catalog.mockResolvedValue({});
    mocks.model.mockResolvedValue({
      tool: "atlas",
      model_dir: "model",
      files: { "components.yaml": "version: 1\n" },
    });
    mocks.data.mockResolvedValue({
      tool: "atlas",
      summary: {},
      kpis: [],
      charts: [],
      tables: [],
      graph: "",
      errors: [],
      warnings: [],
    });
    mocks.artifacts.mockResolvedValue([
      {
        name: "dependency-graph.md",
        label: "Graphe de dépendances",
        kind: "mermaid",
        available: true,
        size: 10,
      },
    ]);
    mocks.schemas.mockResolvedValue({ "components.schema.json": "{}" });
    mocks.scenarios.mockResolvedValue({
      active: "base",
      scenarios: [
        {
          name: "base",
          description: "Modèle d’exemple fourni",
          created_at: "2026-01-01",
          updated_at: "2026-01-01",
          active: true,
          versions: [],
        },
      ],
    });
    mocks.artifact.mockResolvedValue({
      tool: "atlas",
      name: "dependency-graph.md",
      content: "flowchart LR",
    });
    mocks.imports.mockResolvedValue([]);
    mocks.importDiff.mockResolvedValue({
      file: "",
      changed: false,
      current: "",
      proposed: "",
      diff: "",
    });
  });

  it("keeps the tab order and translates the labels without changing routes", async () => {
    window.location.hash = "#/atlas/overview";
    render(<App />);

    await waitFor(() => {
      expect(screen.getAllByRole("tab")).toHaveLength(6);
    });

    expect(screen.getAllByRole("tab").map((tab) => tab.textContent)).toEqual([
      "Vue d’ensemble",
      "Scénarios",
      "Modèle",
      "Sorties",
      "Import",
      "Schémas",
    ]);
    expect(screen.getByRole("heading", { name: "Atlas" })).toBeInTheDocument();
    expect(window.location.hash).toBe("#/atlas/overview");
  });

  it("canonicalizes #/home to the home route", async () => {
    window.location.hash = "#/home";
    render(<App />);

    await waitFor(() => {
      expect(window.location.hash).toBe("#/");
    });
    expect(screen.queryAllByRole("tab")).toHaveLength(0);
    expect(screen.getByText("Les sept outils", { exact: false })).toBeInTheDocument();
  });

  it("falls back to the overview tab for an unknown tab key", async () => {
    window.location.hash = "#/atlas/unknown";
    render(<App />);

    await waitFor(() => {
      expect(window.location.hash).toBe("#/atlas/overview");
    });
    expect(screen.getByRole("tab", { name: "Vue d’ensemble" })).toHaveAttribute(
      "data-state",
      "active",
    );
  });
});
