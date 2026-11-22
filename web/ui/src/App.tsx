import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import * as Tabs from "@radix-ui/react-tabs";
import * as Switch from "@radix-ui/react-switch";
import { AlertCircle, CheckCircle2, RotateCcw, ShieldAlert, Play, Activity } from "lucide-react";
import { api } from "./lib/api";
import type {
  ArtifactInfo,
  ArtifactPayload,
  ModelPayload,
  RunResult,
  ScenarioState,
  TabKey,
  ToolInfo,
  ViewData,
} from "./lib/types";
import { accentFor, cn, displayToolName } from "./lib/utils";
import { ArtifactView } from "./components/ArtifactView";
import { ChartCard } from "./components/ChartCard";
import { DataTable } from "./components/DataTable";
import { FindingsPanel } from "./components/FindingsPanel";
import { FormView } from "./components/FormView";
import { GraphView } from "./components/GraphView";
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

export default function App() {
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [activeToolId, setActiveToolId] = useState("");
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
  const [tab, setTab] = useState<TabKey>("overview");
  const [modelMode, setModelMode] = useState<"form" | "yaml">("form");
  const [busy, setBusy] = useState<"validate" | "check" | "save" | "reset" | "scenario" | null>(null);
  const [error, setError] = useState("");
  const activeIdRef = useRef("");

  const tool = useMemo(
    () => tools.find((entry) => entry.id === activeToolId) ?? null,
    [tools, activeToolId],
  );
  const accent = accentFor(tool?.accent ?? "blue");
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
      setArtifacts(freshArtifacts);
      setActiveArtifact(freshArtifacts.find((entry) => entry.available)?.name ?? "");
      setArtifactVersion((version) => version + 1);
    }
  }, []);

  useEffect(() => {
    api
      .tools()
      .then((items) => {
        setTools(items);
        setActiveToolId(items[0]?.id ?? "");
      })
      .catch((cause: unknown) => setError(String(cause)));
  }, []);

  useEffect(() => {
    if (!activeToolId) return;
    activeIdRef.current = activeToolId;
    setActiveArtifact("");
    setArtifactPayload(null);
    void loadTool(activeToolId, true).catch((cause: unknown) => {
      setError(cause instanceof Error ? cause.message : String(cause));
    });
  }, [activeToolId, loadTool]);

  useEffect(() => {
    if (!activeToolId || !activeArtifact) {
      setArtifactPayload(null);
      return;
    }
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
  const selectedTable = view?.tables.find((entry) => entry.id === activeTable) ?? null;
  const activeScenarioInfo = scenarioState?.scenarios.find((entry) => entry.active) ?? null;

  if (!tools.length) {
    return (
      <div className="grid min-h-screen place-items-center bg-slate-50">
        <div className="text-center">
          <Activity className="mx-auto h-6 w-6 animate-pulse text-slate-400" />
          <p className="mt-3 text-sm text-slate-500">
            {error || "Loading the Fortcloud console…"}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <ToolSidebar tools={tools} activeId={activeToolId} onSelect={setActiveToolId} />

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-slate-200 bg-white px-7 py-5">
          <div className="flex flex-wrap items-start justify-between gap-5">
            <div className="min-w-0">
              <div className="flex items-center gap-2.5">
                <span className={cn("h-2.5 w-2.5 rounded-full", accent.dot)} />
                <h1 className="text-xl font-bold tracking-tight text-slate-900">
                  {displayToolName(tool?.name ?? "")}
                </h1>
                {result && (
                  <Badge tone={result.exit_code === 0 ? "green" : "rose"}>
                    exit {result.exit_code}
                  </Badge>
                )}
              </div>
              <p className="mt-1 text-sm font-medium text-slate-500">{tool?.tagline}</p>
              <p className="mt-1.5 max-w-2xl text-xs leading-relaxed text-slate-400">
                {tool?.description}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="mr-2 flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2">
                <Switch.Root
                  id="strict-mode"
                  checked={strict}
                  onCheckedChange={setStrict}
                  className="relative h-4 w-7 rounded-full bg-slate-300 transition data-[state=checked]:bg-slate-900"
                >
                  <Switch.Thumb className="block h-3 w-3 translate-x-0.5 rounded-full bg-white transition-transform data-[state=checked]:translate-x-3.5" />
                </Switch.Root>
                <label htmlFor="strict-mode" className="cursor-pointer text-2xs font-semibold text-slate-600">
                  Strict
                </label>
              </div>
              <Button onClick={runValidate} loading={busy === "validate"}>
                <ShieldAlert className="h-3.5 w-3.5" />
                Validate
              </Button>
              <Button variant="primary" onClick={runCheck} loading={busy === "check"}>
                <Play className="h-3.5 w-3.5" />
                Check
              </Button>
              <Button aria-label="Reset model" title="Reset to the bundled example" onClick={resetModel} loading={busy === "reset"}>
                <RotateCcw className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>

          {error && (
            <div className="mt-4 flex items-start gap-2 rounded-lg bg-rose-50 px-3 py-2.5 text-xs text-rose-700">
              <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              {error}
            </div>
          )}
        </header>

        <div className="flex-1 px-7 py-6">
          <Tabs.Root value={tab} onValueChange={(value) => setTab(value as TabKey)}>
            <Tabs.List className="inline-flex gap-1 rounded-lg border border-slate-200 bg-white p-1 shadow-sm">
              {TAB_ITEMS.map((item) => (
                <Tabs.Trigger
                  key={item.key}
                  value={item.key}
                  className="rounded-md px-3.5 py-1.5 text-xs font-semibold text-slate-500 transition hover:text-slate-800 data-[state=active]:bg-slate-900 data-[state=active]:text-white"
                >
                  {item.label}
                </Tabs.Trigger>
              ))}
            </Tabs.List>

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
                          className="rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-2xs font-semibold text-slate-700 outline-none focus:border-slate-400 disabled:opacity-50"
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
                              "rounded-full border px-3 py-1.5 text-2xs font-semibold transition",
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

                <Tabs.Content value="scenarios" className="animate-fade-in outline-none">
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
                            "rounded-md px-3.5 py-1.5 text-xs font-semibold transition",
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
                        ? "Fill in the fields, then save. Validation still runs through the tool."
                        : "Edit the YAML directly, then Save. Check regenerates the artifacts."}
                    </p>
                  </div>

                  {modelMode === "form" ? (
                    <FormView
                      toolId={activeToolId}
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
                              "rounded-lg border px-3 py-2 font-mono text-2xs font-semibold transition",
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

                <Tabs.Content value="outputs" className="animate-fade-in outline-none">
                  {artifacts.length ? (
                    <div className="grid gap-5 lg:grid-cols-[230px_minmax(0,1fr)]">
                      <div className="space-y-1.5">
                        {artifacts.map((artifact) => (
                          <button
                            key={artifact.name}
                            disabled={!artifact.available}
                            onClick={() => setActiveArtifact(artifact.name)}
                            className={cn(
                              "flex w-full items-center justify-between gap-2 rounded-lg border px-3 py-2.5 text-left transition disabled:opacity-40",
                              artifact.name === activeArtifact
                                ? "border-slate-900 bg-white shadow-sm"
                                : "border-transparent bg-white/60 hover:border-slate-200 hover:bg-white",
                            )}
                          >
                            <span className="min-w-0">
                              <span className="block truncate text-xs font-semibold text-slate-700">
                                {artifact.label}
                              </span>
                              <span className="block truncate font-mono text-3xs text-slate-400">
                                {artifact.name}
                              </span>
                            </span>
                            {artifact.available && <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-500" />}
                          </button>
                        ))}
                      </div>
                      {selectedArtifact && <ArtifactView artifact={selectedArtifact} payload={artifactPayload} />}
                    </div>
                  ) : (
                    <EmptyState title="No artifacts" hint="Run Check to generate the reports for this tool." />
                  )}
                </Tabs.Content>

                <Tabs.Content value="import" className="animate-fade-in outline-none">
                  <ImportView
                    toolId={activeToolId}
                    files={modelFiles}
                    onAccepted={() => loadTool(activeToolId, true)}
                  />
                </Tabs.Content>

                <Tabs.Content value="schemas" className="animate-fade-in outline-none">
                  <div className="mb-4 flex flex-wrap gap-2">
                    {Object.keys(schemas).map((filename) => (
                      <button
                        key={filename}
                        onClick={() => setActiveSchema(filename)}
                        className={cn(
                          "rounded-lg border px-3 py-2 font-mono text-2xs font-semibold transition",
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
                    <pre className="max-h-[600px] overflow-auto rounded-lg bg-slate-950 p-4 font-mono text-2xs leading-relaxed text-slate-200">
                      {activeSchema ? schemas[activeSchema] : "No schema available."}
                    </pre>
                  </div>
                </Tabs.Content>
              </div>

              <aside className="min-w-0">
                <FindingsPanel result={result} />
              </aside>
            </div>
          </Tabs.Root>
        </div>
      </main>
    </div>
  );
}
