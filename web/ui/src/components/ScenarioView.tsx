import { useCallback, useEffect, useState } from "react";
import { Camera, GitCompare, Plus, RotateCcw, Trash2 } from "lucide-react";
import { api } from "../lib/api";
import type { ScenarioState } from "../lib/types";
import { cn } from "../lib/utils";
import { Badge, Button, Card, CardTitle } from "./ui";

function dateLabel(value: string): string {
  if (!value) return "bundled";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export function ScenarioView({
  toolId,
  active,
  state,
  onChanged,
}: {
  toolId: string;
  active: boolean;
  state: ScenarioState | null;
  onChanged: (state: ScenarioState) => void;
}) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [label, setLabel] = useState("");
  const [left, setLeft] = useState("current");
  const [right, setRight] = useState("");
  const [diff, setDiff] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const scenarios = state?.scenarios ?? [];
  const activeScenario = scenarios.find((item) => item.active)?.name ?? "base";
  const versions = scenarios.find((item) => item.name === activeScenario)?.versions ?? [];

  useEffect(() => {
    setRight(versions.length ? `${activeScenario}:${versions[versions.length - 1].version}` : "base");
  }, [activeScenario, versions]);

  const run = useCallback(
    async (action: () => Promise<ScenarioState>) => {
      setBusy(true);
      setError("");
      try {
        onChanged(await action());
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : String(cause));
      } finally {
        setBusy(false);
      }
    },
    [onChanged],
  );

  const runCompare = useCallback(async () => {
    if (!right) return;
    setBusy(true);
    setError("");
    try {
      const result = await api.compare(toolId, left, right);
      const lines = result.files.flatMap((file) =>
        file.changed ? [`### ${file.file}`, file.diff] : [],
      );
      setDiff(lines.join("\n\n") || "No differences between these versions.");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(false);
    }
  }, [toolId, left, right]);

  if (!active) return null;

  const options = [
    { value: "current", label: "Current live model" },
    ...scenarios.flatMap((scenario) => [
      { value: scenario.name, label: `${scenario.name} · latest` },
      ...scenario.versions.map((version) => ({
        value: `${scenario.name}:${version.version}`,
        label: `${scenario.name} · v${version.version}${version.label ? ` · ${version.label}` : ""}`,
      })),
    ]),
  ];

  return (
    <div className="space-y-5">
      <div className="rounded-lg border border-sky-100 bg-sky-50 px-3.5 py-2.5 text-2xs leading-relaxed text-sky-900">
        Scenarios keep independent copies of this tool's model. Switching one restores its latest
        version; <span className="font-semibold">Snapshot</span> records the current files as a new
        version before you continue.
      </div>

      {error && (
        <div className="rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">{error}</div>
      )}

      <Card>
        <CardTitle
          title="Scenarios"
          subtitle={`Active: ${activeScenario}`}
          action={<Badge tone="blue">{scenarios.length} total</Badge>}
        />
        <div className="divide-y divide-slate-100">
          {scenarios.map((scenario) => (
            <div
              key={scenario.name}
              className={cn(
                "flex flex-wrap items-center justify-between gap-3 py-2.5",
                scenario.active && "text-slate-900",
              )}
            >
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-semibold">{scenario.name}</span>
                  {scenario.active && <Badge tone="green">active</Badge>}
                  <span className="text-3xs text-slate-400">
                    {scenario.versions.length} version{scenario.versions.length === 1 ? "" : "s"}
                  </span>
                </div>
                {scenario.description && (
                  <p className="mt-0.5 text-2xs text-slate-500">{scenario.description}</p>
                )}
                <p className="mt-0.5 text-3xs text-slate-400">
                  Updated {dateLabel(scenario.updated_at || scenario.created_at)}
                </p>
              </div>
              <div className="flex items-center gap-1.5">
                {!scenario.active && (
                  <Button
                    disabled={busy}
                    onClick={() => run(() => api.activateScenario(toolId, scenario.name))}
                  >
                    <RotateCcw className="h-3 w-3" /> Activate
                  </Button>
                )}
                {scenario.name !== "base" && (
                  <Button
                    disabled={busy}
                    onClick={() => run(() => api.deleteScenario(toolId, scenario.name))}
                  >
                    <Trash2 className="h-3 w-3" /> Delete
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap items-end gap-2 border-t border-slate-100 pt-4">
          <label className="min-w-[180px] flex-1">
            <span className="mb-1 block text-3xs font-semibold uppercase tracking-wider text-slate-500">
              New scenario
            </span>
            <input
              className="form-control w-full"
              value={name}
              placeholder="e.g. cost-optimisation"
              onChange={(event) => setName(event.target.value)}
            />
          </label>
          <label className="min-w-[220px] flex-1">
            <span className="mb-1 block text-3xs font-semibold uppercase tracking-wider text-slate-500">
              Description
            </span>
            <input
              className="form-control w-full"
              value={description}
              placeholder="Optional"
              onChange={(event) => setDescription(event.target.value)}
            />
          </label>
          <Button
            variant="primary"
            disabled={busy || !name.trim()}
            onClick={() =>
              run(async () => {
                const next = await api.createScenario(toolId, name.trim(), description.trim());
                setName("");
                setDescription("");
                return next;
              })
            }
          >
            <Plus className="h-3 w-3" /> Create
          </Button>
        </div>
      </Card>

      <Card>
        <CardTitle
          title="Version history"
          subtitle={`Snapshots of ${activeScenario}`}
          action={
            <div className="flex items-center gap-2">
              <input
                className="form-control w-40"
                value={label}
                placeholder="Label (optional)"
                onChange={(event) => setLabel(event.target.value)}
              />
              <Button
                disabled={busy}
                onClick={() =>
                  run(async () => {
                    const next = await api.snapshot(toolId, label.trim());
                    setLabel("");
                    return next;
                  })
                }
              >
                <Camera className="h-3 w-3" /> Snapshot
              </Button>
            </div>
          }
        />
        {versions.length ? (
          <div className="divide-y divide-slate-100">
            {[...versions].reverse().map((version) => (
              <div
                key={version.version}
                className="flex items-center justify-between gap-3 py-2 text-xs"
              >
                <span className="font-mono font-semibold text-slate-700">
                  v{version.version.toString().padStart(3, "0")}
                </span>
                <span className="min-w-0 flex-1 truncate text-slate-500">
                  {version.label || "Automatic version"}
                </span>
                <span className="text-3xs text-slate-400">{dateLabel(version.created_at)}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500">No snapshot yet in this scenario.</p>
        )}
      </Card>

      <Card>
        <CardTitle title="Compare" subtitle="Unified diff of two model states" />
        <div className="flex flex-wrap items-end gap-2">
          <label className="min-w-[200px] flex-1">
            <span className="mb-1 block text-3xs font-semibold uppercase tracking-wider text-slate-500">
              From
            </span>
            <select
              className="form-control w-full"
              value={left}
              onChange={(event) => setLeft(event.target.value)}
            >
              {options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label className="min-w-[200px] flex-1">
            <span className="mb-1 block text-3xs font-semibold uppercase tracking-wider text-slate-500">
              To
            </span>
            <select
              className="form-control w-full"
              value={right}
              onChange={(event) => setRight(event.target.value)}
            >
              {options.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <Button variant="primary" disabled={busy || !right} onClick={runCompare}>
            <GitCompare className="h-3 w-3" /> Compare
          </Button>
        </div>
        {diff && (
          <pre className="mt-4 max-h-[420px] overflow-auto rounded-lg bg-slate-950 p-3 font-mono text-3xs leading-relaxed text-slate-200">
            {diff}
          </pre>
        )}
      </Card>
    </div>
  );
}
