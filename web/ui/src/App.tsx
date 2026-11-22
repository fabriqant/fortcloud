import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import * as Tabs from "@radix-ui/react-tabs";
import * as Switch from "@radix-ui/react-switch";
import { Activity, AlertCircle, CheckCircle2, Cloud, Database, Play, RotateCcw, ShieldAlert } from "lucide-react";
import { api } from "./lib/api";
import { toolIcon } from "./lib/toolIcons";
import type {
  ArtifactInfo,
  ArtifactPayload,
  Catalog,
  ModelPayload,
  RunResult,
  ScenarioState,
  TabKey,
  ToolInfo,
  ViewData,
} from "./lib/types";
import { accentFor, cn, displayToolName } from "./lib/utils";
import { ArtifactView } from "./components/ArtifactView";
import { CatalogModal } from "./components/CatalogModal";
import { ConnectorModal } from "./components/ConnectorModal";
import { ChartCard } from "./components/ChartCard";
import { DataTable } from "./components/DataTable";
import { FindingsPanel } from "./components/FindingsPanel";
import { FormView } from "./components/FormView";
import { GraphView } from "./components/GraphView";
import { HomePage } from "./components/HomePage";
import { ImportView } from "./components/ImportView";
import { KpiCards } from "./components/KpiCards";
import { ModelEditor } from "./components/ModelEditor";
import { ScenarioView } from "./components/ScenarioView";
import { ToolSidebar } from "./components/ToolSidebar";
import { Badge, Button, EmptyState } from "./components/ui";

const TAB_ITEMS: { key: TabKey; label: string }[] = [
  { key: "overview", label: "Overview" },
  { key: "scenarios", label: "Scenarios" },
  { key: "model", label: "Model" },
  { key: "outputs", label: "Outputs" },
  { key: "import", label: "Import" },
  { key: "schemas", label: "Schemas" },
];

const TAB_KEYS = new Set<string>(TAB_ITEMS.map((item) => item.key));

const TAB_INTRO: Record<TabKey, string> = {
  overview: "Live KPIs, flow and findings for the active scenario.",
  scenarios: "Reviewable branches with versions you can restore or compare.",
  model: "Edit the YAML model with guided fields or directly in source.",
  outputs: "Reports and status rebuilt from the model by Check.",
  import: "Stage a local YAML proposal, review the diff, then accept it.",
  schemas: "The JSON Schemas that validate the model and drive the guided form.",
};

type Route =
  | { home: true; toolId: ""; tab: TabKey }
  | { home: false; toolId: string; tab: TabKey };

function readRoute(): Route {
  const hash = window.location.hash;
  if (!hash || hash === "#/" || hash === "#/home") {
    return { home: true, toolId: "", tab: "overview" };
  }
  const match = hash.match(/^#\/([^/]+)(?:\/([^/]+))?$/);
  const candidate = match?.[2];
  return {
    home: false,
    toolId: match?.[1] ?? "",
    tab: candidate && TAB_KEYS.has(candidate) ? (candidate as TabKey) : "overview",
  };
}

export default function App() {
  const [initialRoute] = useState(readRoute);
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [suiteVersion, setSuiteVersion] = useState("0.1.0");
  const [home, setHome] = useState(initialRoute.home);
  const [activeToolId, setActiveToolId] = useState(initialRoute.home ? "" : initialRoute.toolId);
  const [model, setModel] = useState<ModelPayload | null>(null);
  const [draft, setDraft] = useState<Record<string, string>>({});
  const [view, setView] = useState<ViewData | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactInfo[]>([]);
  const [activeArtifact, setActiveArtifact] = useState("");
  const [artifactPayload, setArtifactPayload] = useState<ArtifactPayload | null>(null);
  const [artifactVersion, setArtifactVersion] = useState(0);
  const [scenarioState, setScenarioState] = useState<ScenarioState | null>(null);
  const [schemas, setSchemas] = useState<Record<string, string>>({});
  const [activeSchema, setActiveSchema] = useState("");
  const [activeFile, setActiveFile] = useState("");
  const [activeTable, setActiveTable] = useState("");
  const [result, setResult] = useState<RunResult | null>(null);
  const [strict, setStrict] = useState(false);
  const [catalog, setCatalog] = useState<Catalog>({});
  const [catalogOpen, setCatalogOpen] = useState(false);
  const [connectorOpen, setConnectorOpen] = useState(false);
  const [tab, setTab] = useState<TabKey>(initialRoute.tab);
  const [modelMode, setModelMode] = useState<"form" | "yaml">("form");
  const [busy, setBusy] = useState<"validate" | "check" | "save" | "reset" | "scenario" | null>(null);
  const [error, setError] = useState("");
  const activeIdRef = useRef("");
  const artifactToolRef = useRef("");
  const wasHomeRef = useRef(home);

  useLayoutEffect(() => {
    if (wasHomeRef.current && !home) window.scrollTo(0, 0);
    wasHomeRef.current = home;
  }, [home]);

  const tool = useMemo(
    () => tools.find((entry) => entry.id === activeToolId) ?? null,
    [tools, activeToolId],
  );
  const accent = accentFor(tool?.accent ?? "blue");
  const ToolIcon = toolIcon(tool?.icon);
  const modelFiles = useMemo(() => Object.keys(model?.files ?? {}), [model]);

  const loadTool = useCallback(async (toolId: string, clearResult: boolean) => {
    if (clearResult) setResult(null);
    setError("");
    const [modelPayload, data, artifactList, schemaMap, scenarios] = await Promise.all([
      api.model(toolId),
      api.data(toolId),
      api.artifacts(toolId),
      api.schemas(toolId),
      api.scenarios(toolId),
    ]);
    if (activeIdRef.current !== toolId) return;

    setModel(modelPayload);
    setScenarioState(scenarios);
    setDraft({ ...modelPayload.files });
    setActiveFile(Object.keys(modelPayload.files)[0] ?? "");
    setView(data);
    setActiveTable(data.tables[0]?.id ?? "");
    artifactToolRef.current = toolId;
    setArtifacts(artifactList);
    setActiveArtifact(artifactList.find((entry) => entry.available)?.name ?? "");
    setSchemas(schemaMap);
    setActiveSchema(Object.keys(schemaMap)[0] ?? "");

    if (artifactList.length && artifactList.every((entry) => !entry.available)) {
      const outcome = await api.check(toolId, false);
      if (activeIdRef.current !== toolId) return;
      setResult(outcome);
      const [freshData, freshArtifacts] = await Promise.all([
        api.data(toolId),
        api.artifacts(toolId),
      ]);
      if (activeIdRef.current !== toolId) return;
      setView(freshData);
      setActiveTable(freshData.tables[0]?.id ?? "");
      artifactToolRef.current = toolId;
      setArtifacts(freshArtifacts);
      setActiveArtifact(freshArtifacts.find((entry) => entry.available)?.name ?? "");
      setArtifactVersion((version) => version + 1);
    }
  }, []);

  const navigate = useCallback((toolId: string, tabKey: TabKey = "overview") => {
    const next = `#/${toolId}/${tabKey}`;
    setHome(false);
    setActiveToolId(toolId);
    setTab(tabKey);
    if (window.location.hash !== next) window.location.hash = next;
  }, []);

  const navigateHome = useCallback(() => {
    setHome(true);
    if (window.location.hash !== "#/") window.location.hash = "#/";
  }, []);

  useEffect(() => {
    api
      .tools()
      .then(setTools)
      .catch((cause: unknown) => setError(String(cause)));
  }, []);

  useEffect(() => {
    api
      .health()
      .then((info) => setSuiteVersion(info.version))
      .catch(() => {
        // The bundled fallback is enough if health is unavailable.
      });
  }, []);

  useEffect(() => {
    api
      .catalog()
      .then(setCatalog)
      .catch(() => {
        // Suggestions remain optional if the catalog is unavailable.
      });
  }, []);

  useEffect(() => {
    if (!tools.length) return;
    const route = readRoute();
    if (route.home) {
      setHome(true);
      if (window.location.hash !== "#/") window.history.replaceState(null, "", "#/");
      return;
    }
    const toolId = tools.some((entry) => entry.id === route.toolId) ? route.toolId : "";
    if (!toolId) {
      setHome(true);
      window.history.replaceState(null, "", "#/");
      return;
    }
    const next = `#/${toolId}/${route.tab}`;
    if (window.location.hash !== next) window.history.replaceState(null, "", next);
    setHome(false);
    setActiveToolId(toolId);
    setTab(route.tab);
  }, [tools]);

  useEffect(() => {
    const onHashChange = () => {
      const route = readRoute();
      if (route.home) {
        setHome(true);
        if (window.location.hash !== "#/") window.history.replaceState(null, "", "#/");
        return;
      }
      const toolId = tools.some((entry) => entry.id === route.toolId) ? route.toolId : "";
      if (!toolId) {
        setHome(true);
        window.history.replaceState(null, "", "#/");
        return;
      }
      const next = `#/${toolId}/${route.tab}`;
      if (window.location.hash !== next) window.history.replaceState(null, "", next);
      setHome(false);
      setTab(route.tab);
      setActiveToolId(toolId);
    };
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, [tools]);

  useEffect(() => {
    if (home || !activeToolId) return;
    activeIdRef.current = activeToolId;
    artifactToolRef.current = "";
    setActiveArtifact("");
    setArtifactPayload(null);
    void loadTool(activeToolId, true).catch((cause: unknown) => {
      setError(cause instanceof Error ? cause.message : String(cause));
    });
  }, [home, activeToolId, loadTool]);

  useEffect(() => {
    if (!activeToolId || !activeArtifact || artifactToolRef.current !== activeToolId) {
      setArtifactPayload(null);
      return;
    }
    setArtifactPayload(null);
    let cancelled = false;
    api
      .artifact(activeToolId, activeArtifact)
      .then((payload) => {
        if (!cancelled) setArtifactPayload(payload);
      })
      .catch(() => {
        if (!cancelled) setArtifactPayload(null);
      });
    return () => {
      cancelled = true;
    };
  }, [activeToolId, activeArtifact, artifactVersion]);

  const runValidate = useCallback(async () => {
    if (!activeToolId) return;
    setBusy("validate");
    setError("");
    try {
      const outcome = await api.validate(activeToolId, strict);
      setResult(outcome);
      const data = await api.data(activeToolId);
      setView(data);
      setActiveTable((current) => data.tables.some((t) => t.id === current) ? current : data.tables[0]?.id ?? "");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(null);
    }
  }, [activeToolId, strict]);

  const runCheck = useCallback(async () => {
    if (!activeToolId) return;
    setBusy("check");
    setError("");
    try {
      const outcome = await api.check(activeToolId, strict);
      setResult(outcome);
      const [data, artifactList] = await Promise.all([
        api.data(activeToolId),
        api.artifacts(activeToolId),
      ]);
      setView(data);
      setActiveTable((current) => data.tables.some((t) => t.id === current) ? current : data.tables[0]?.id ?? "");
      artifactToolRef.current = activeToolId;
      setArtifacts(artifactList);
      setActiveArtifact(artifactList.find((entry) => entry.available)?.name ?? "");
      setArtifactVersion((version) => version + 1);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(null);
    }
  }, [activeToolId, strict]);

  const recordSnapshot = useCallback(
    async (label: string) => {
      if (!activeToolId) return;
      try {
        const next = await api.snapshot(activeToolId, label);
        if (activeIdRef.current === activeToolId) setScenarioState(next);
      } catch {
        // Versioning is best-effort; a failed snapshot must never block a save.
      }
    },
    [activeToolId],
  );

  const saveFile = useCallback(async () => {
    if (!activeToolId || !activeFile) return;
    setBusy("save");
    try {
      await api.saveFile(activeToolId, activeFile, draft[activeFile] ?? "");
      setModel((current) =>
        current
          ? { ...current, files: { ...current.files, [activeFile]: draft[activeFile] ?? "" } }
          : current,
      );
      await recordSnapshot(`Saved ${activeFile}`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(null);
    }
  }, [activeToolId, activeFile, draft, recordSnapshot]);

  const resetModel = useCallback(async () => {
    if (!activeToolId) return;
    setBusy("reset");
    setError("");
    try {
      await api.reset(activeToolId);
      await loadTool(activeToolId, true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(null);
    }
  }, [activeToolId, loadTool]);

  const selectScenario = useCallback(
    async (name: string) => {
      if (!activeToolId || name === scenarioState?.active) return;
      setBusy("scenario");
      setError("");
      try {
        const next = await api.activateScenario(activeToolId, name);
        if (activeIdRef.current !== activeToolId) return;
        setScenarioState(next);
        await loadTool(activeToolId, true);
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause));
      } finally {
        setBusy(null);
      }
    },
    [activeToolId, loadTool, scenarioState?.active],
  );

  const dirty = Boolean(activeFile && model && draft[activeFile] !== model.files[activeFile]);
  const selectedArtifact = artifacts.find((entry) => entry.name === activeArtifact) ?? null;
  const visiblePayload =
    selectedArtifact && artifactPayload?.name === selectedArtifact.name ? artifactPayload : null;
  const selectedTable = view?.tables.find((entry) => entry.id === activeTable) ?? null;
  const activeScenarioInfo = scenarioState?.scenarios.find((entry) => entry.active) ?? null;

  if (!tools.length) {
    return (
      <div className="grid min-h-screen place-items-center bg-slate-50">
        <div className="text-center">
          <Activity className="mx-auto h-6 w-6 animate-pulse text-slate-400" />
          <p className="mt-3 text-sm text-slate-500">
            {error || "Loading the FortCloud console…"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <ToolSidebar
        tools={tools}
        activeId={activeToolId}
        home={home}
        version={suiteVersion}
        onHome={navigateHome}
        onSelect={(id) => navigate(id, "overview")}
      />

      <main className="flex min-w-0 flex-1 flex-col">
        <div key={home ? "home" : activeToolId} className="animate-tool-in flex min-h-0 flex-1 flex-col">
          {home ? (
            <HomePage tools={tools} version={suiteVersion} onOpenTool={(id) => navigate(id)} />
          ) : (
            <>
              <header
                className={cn(
                  "border-b border-white/20 px-7 py-5",
                  accent.solid,
                )}
              >
                <div className="flex flex-wrap items-start justify-between gap-5">
                  <div className="min-w-0">
                    <div className="flex items-center gap-3.5">
                      <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-white/15 text-white ring-1 ring-white/25">
                        <ToolIcon className="h-5 w-5" />
                      </span>
                      <h1 className="text-xl font-bold tracking-tight text-white">
                        {displayToolName(tool?.name ?? "")}
                      </h1>
                      {result && (
                        <Badge tone={result.exit_code === 0 ? "green" : "rose"}>
                          exit {result.exit_code}
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <Button
                      variant="ghost"
                      className="text-white/80 hover:bg-white/15 hover:text-white focus:ring-white/60"
                      onClick={() => setConnectorOpen(true)}
                    >
                      <Cloud className="h-3.5 w-3.5" />
                      Cloud connectors
                    </Button>
                    <Button
                      variant="ghost"
                      className="text-white/80 hover:bg-white/15 hover:text-white focus:ring-white/60"
                      onClick={() => setCatalogOpen(true)}
                    >
                      <Database className="h-3.5 w-3.5" />
                      Reference data
                    </Button>
                    <div className="mr-2 flex items-center gap-2 rounded-lg border border-white/30 bg-white/10 px-3 py-2">
                      <Switch.Root
                        id="strict-mode"
                        checked={strict}
                        onCheckedChange={setStrict}
                        className="group relative h-4 w-7 rounded-full bg-white/30 transition data-[state=checked]:bg-white"
                      >
                        <Switch.Thumb className="block h-3 w-3 translate-x-0.5 rounded-full bg-white transition-transform group-data-[state=checked]:translate-x-3.5 group-data-[state=checked]:bg-slate-800" />
                      </Switch.Root>
                      <label htmlFor="strict-mode" className="cursor-pointer text-2xs font-semibold text-white/80">
                        Strict
                      </label>
                    </div>
                    <Button
                      className="border-white/30 bg-white/10 text-white hover:bg-white/20 focus:ring-white/60"
                      onClick={runValidate}
                      loading={busy === "validate"}
                    >
                      <ShieldAlert className="h-3.5 w-3.5" />
                      Validate
                    </Button>
                    <Button
                      variant="primary"
                      className={cn("bg-white hover:bg-white/90 focus:ring-white/70", accent.text)}
                      onClick={runCheck}
                      loading={busy === "check"}
                    >
                      <Play className="h-3.5 w-3.5" />
                      Check
                    </Button>
                    <Button
                      aria-label="Reset model"
                      title="Reset to the bundled example"
                      className="border-white/30 bg-white/10 text-white hover:bg-white/20 focus:ring-white/60"
                      onClick={resetModel}
                      loading={busy === "reset"}
                    >
                      <RotateCcw className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>

                {error && (
                  <div className="mt-4 flex items-start gap-2 rounded-lg bg-white/15 px-3 py-2.5 text-xs text-white ring-1 ring-white/25">
                    <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                    {error}
                  </div>
                )}
              </header>

          <div className="flex-1 px-7 py-6">
            {tool?.description && (
              <p className="mx-auto mt-12 mb-20 max-w-4xl text-center text-lg font-medium leading-relaxed text-slate-600">
                {tool.description}
              </p>
            )}
            <Tabs.Root value={tab} onValueChange={(value) => navigate(activeToolId, value as TabKey)}>
              <Tabs.List className="inline-flex gap-1 rounded-lg border border-slate-200 bg-white p-1 shadow-sm">
                {TAB_ITEMS.map((item) => (
                  <Tabs.Trigger
                    key={item.key}
                    value={item.key}
                    className="content-button text-slate-500 hover:text-slate-800 data-[state=active]:bg-slate-900 data-[state=active]:text-white"
                  >
                    {item.label}
                  </Tabs.Trigger>
                ))}
              </Tabs.List>
              <p className="mt-3 max-w-5xl text-2xs leading-relaxed text-slate-500">
                {TAB_INTRO[tab]}
              </p>

              <div className="mt-5 grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1fr)_300px]">
                <div className="min-w-0">
                  <Tabs.Content value="overview" className="animate-fade-in space-y-5 outline-none">
                    {activeScenarioInfo && (
                      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-5 py-3 shadow-card">
                        <div>
                          <p className="text-3xs font-semibold uppercase tracking-wider text-slate-400">
                            Scenario
                          </p>
                          <p className="mt-0.5 text-sm font-semibold text-slate-800">
                            {activeScenarioInfo.name}
                          </p>
                          <p className="mt-0.5 text-2xs text-slate-500">
                            {activeScenarioInfo.description || "Bundled example model"}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <select
                            aria-label="Active scenario"
                            disabled={busy === "scenario"}
                            value={activeScenarioInfo.name}
                            onChange={(event) => void selectScenario(event.target.value)}
                            className="form-control disabled:opacity-50"
                          >
                            {scenarioState?.scenarios.map((scenario) => (
                              <option key={scenario.name} value={scenario.name}>
                                {scenario.name}
                                {scenario.versions.length
                                  ? ` · v${scenario.versions[scenario.versions.length - 1].version}`
                                  : ""}
                              </option>
                            ))}
                          </select>
                          <Badge tone="blue">
                            {activeScenarioInfo.versions.length} version
                            {activeScenarioInfo.versions.length === 1 ? "" : "s"}
                          </Badge>
                        </div>
                      </div>
                    )}

                    <p className="text-2xs leading-relaxed text-slate-500">
                      Switching the branch changes every number below. Run Check after a model change
                      to refresh the charts and tables.
                    </p>

                    <KpiCards kpis={view?.kpis ?? []} />

                    {view?.graph && <GraphView graph={view.graph} />}

                    {Boolean(view?.charts.length) && (
                      <div className={cn("grid gap-5", view && view.charts.length > 1 ? "lg:grid-cols-2" : "")}>
                        {view?.charts.map((chart) => (
                          <ChartCard key={chart.id} chart={chart} />
                        ))}
                      </div>
                    )}

                    {view?.tables.length ? (
                      <>
                        <div className="flex flex-wrap gap-2">
                          {view.tables.map((table) => (
                            <button
                              key={table.id}
                              onClick={() => setActiveTable(table.id)}
                              className={cn(
                                "content-button rounded-full",
                                table.id === activeTable
                                  ? "border-slate-900 bg-slate-900 text-white"
                                  : "border-slate-200 bg-white text-slate-500 hover:border-slate-300 hover:text-slate-800",
                              )}
                            >
                              {table.label} · {table.total}
                            </button>
                          ))}
                        </div>
                        {selectedTable && <DataTable table={selectedTable} />}
                      </>
                    ) : (
                      <EmptyState
                        title="No structured tables yet"
                        hint="Run Check to generate the artifacts, then the tables appear here."
                      />
                    )}
                  </Tabs.Content>

                  <Tabs.Content value="scenarios" className="animate-fade-in space-y-5 outline-none">
                    <p className="text-2xs leading-relaxed text-slate-500">
                      The protected base is the bundled starting point. Named scenarios keep
                      independent copies; activating one clears stale artifacts until Check runs again.
                    </p>
                    <ScenarioView
                      toolId={activeToolId}
                      active={tab === "scenarios"}
                      state={scenarioState}
                      onChanged={(next) => {
                        setScenarioState(next);
                        void loadTool(activeToolId, true).catch((cause: unknown) => {
                          setError(cause instanceof Error ? cause.message : String(cause));
                        });
                      }}
                    />
                  </Tabs.Content>

                  <Tabs.Content value="model" className="animate-fade-in space-y-5 outline-none">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="inline-flex gap-1 rounded-lg border border-slate-200 bg-white p-1 shadow-sm">
                        {(["form", "yaml"] as const).map((mode) => (
                          <button
                            key={mode}
                            onClick={() => setModelMode(mode)}
                            className={cn(
                              "content-button",
                              mode === modelMode
                                ? "bg-slate-900 text-white"
                                : "text-slate-500 hover:text-slate-800",
                            )}
                          >
                            {mode === "form" ? "Guided form" : "YAML source"}
                          </button>
                        ))}
                      </div>
                      <p className="max-w-md text-2xs leading-relaxed text-slate-500">
                        {modelMode === "form"
                          ? "Fields suggest catalog values but accept custom entries. Every save creates a version in the active scenario."
                          : "Edit the YAML directly, then Save. Every save creates a version; Check regenerates the artifacts."}
                      </p>
                    </div>

                    {modelMode === "form" ? (
                      <FormView
                        toolId={activeToolId}
                        catalog={catalog}
                        onSaved={async () => {
                          await recordSnapshot("Guided form save");
                          await loadTool(activeToolId, true);
                        }}
                      />
                    ) : (
                      <>
                        <div className="rounded-lg border border-sky-100 bg-sky-50 px-3.5 py-2.5 text-2xs leading-relaxed text-sky-900">
                          Edit a YAML file below, then select <span className="font-semibold">Save</span>. The
                          model changes only after <span className="font-semibold">Check</span> regenerates the
                          artifacts. Use <span className="font-semibold">Reset</span> to restore the bundled
                          example as a starting template.
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {modelFiles.map((filename) => (
                            <button
                              key={filename}
                              onClick={() => setActiveFile(filename)}
                              className={cn(
                                "content-button font-mono",
                                filename === activeFile
                                  ? "border-slate-900 bg-slate-900 text-white"
                                  : "border-slate-200 bg-white text-slate-500 hover:text-slate-800",
                              )}
                            >
                              {filename}
                              {draft[filename] !== model?.files[filename] && (
                                <span className="ml-2 text-amber-400">●</span>
                              )}
                            </button>
                          ))}
                        </div>
                        {activeFile && (
                          <ModelEditor
                            file={activeFile}
                            value={draft[activeFile] ?? ""}
                            dirty={dirty}
                            saving={busy === "save"}
                            onChange={(value) => setDraft((current) => ({ ...current, [activeFile]: value }))}
                            onSave={saveFile}
                          />
                        )}
                      </>
                    )}
                  </Tabs.Content>

                  <Tabs.Content value="outputs" className="animate-fade-in space-y-5 outline-none">
                    {artifacts.length ? (
                      <>
                        <p className="text-2xs leading-relaxed text-slate-500">
                          Greyed-out artifacts have not been produced for this scenario yet — run Check
                          first. Markdown reports and Mermaid graphs sit alongside machine-readable
                          JSON status.
                        </p>
                        <div className="grid gap-5 lg:grid-cols-[230px_minmax(0,1fr)]">
                          <div className="space-y-1.5">
                            {artifacts.map((artifact) => (
                              <button
                                key={artifact.name}
                                disabled={!artifact.available}
                                onClick={() => setActiveArtifact(artifact.name)}
                                title={artifact.name}
                                className={cn(
                                  "content-button w-full justify-between text-left disabled:opacity-40",
                                  artifact.name === activeArtifact
                                    ? "border-slate-900 bg-white text-slate-900 shadow-sm"
                                    : "border-transparent bg-white/60 text-slate-600 hover:border-slate-200 hover:bg-white hover:text-slate-800",
                                )}
                              >
                                <span className="truncate">{artifact.label}</span>
                                {artifact.available && <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-500" />}
                              </button>
                            ))}
                          </div>
                          {selectedArtifact && <ArtifactView artifact={selectedArtifact} payload={visiblePayload} />}
                        </div>
                      </>
                    ) : (
                      <EmptyState title="No artifacts" hint="Run Check to generate the reports for this tool." />
                    )}
                  </Tabs.Content>

                  <Tabs.Content value="import" className="animate-fade-in space-y-5 outline-none">
                    <ImportView
                      toolId={activeToolId}
                      files={modelFiles}
                      onAccepted={() => loadTool(activeToolId, true)}
                    />
                  </Tabs.Content>

                  <Tabs.Content value="schemas" className="animate-fade-in space-y-4 outline-none">
                    <p className="text-2xs leading-relaxed text-slate-500">
                      Each schema maps to one model file. Required fields, enums and bounds are
                      defined here; catalog values are suggestions, not limits.
                    </p>
                    <div className="mb-4 flex flex-wrap gap-2">
                      {Object.keys(schemas).map((filename) => (
                        <button
                          key={filename}
                          onClick={() => setActiveSchema(filename)}
                          className={cn(
                            "content-button font-mono",
                            filename === activeSchema
                              ? "border-slate-900 bg-slate-900 text-white"
                              : "border-slate-200 bg-white text-slate-500 hover:text-slate-800",
                          )}
                        >
                          {filename}
                        </button>
                      ))}
                    </div>
                    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-card">
                      <h2 className="mb-3 text-sm font-semibold">{activeSchema || "JSON Schema"}</h2>
                      <pre className="max-h-[780px] overflow-auto rounded-lg bg-slate-950 p-4 font-mono text-2xs leading-relaxed text-slate-200">
                        {activeSchema ? schemas[activeSchema] : "No schema available."}
                      </pre>
                    </div>
                  </Tabs.Content>
                </div>

                <aside className="min-w-0 space-y-3">
                  <FindingsPanel result={result} />
                </aside>
              </div>
              </Tabs.Root>
            </div>
            </>
          )}
        </div>
      </main>
      {catalogOpen && (
        <CatalogModal
          catalog={catalog}
          onClose={() => setCatalogOpen(false)}
          onChange={setCatalog}
        />
      )}
      {connectorOpen && (
        <ConnectorModal
          onClose={() => setConnectorOpen(false)}
          onOpenImport={() => {
            setConnectorOpen(false);
            navigate("atlas", "import");
          }}
        />
      )}
    </div>
  );
}
