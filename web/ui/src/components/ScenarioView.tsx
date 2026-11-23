import { useCallback, useEffect, useState } from "react";
import { Trans, useTranslation } from "react-i18next";
import { Camera, GitCompare, Plus, RotateCcw, Trash2 } from "lucide-react";
import { api } from "../lib/api";
import type { ScenarioState } from "../lib/types";
import { cn } from "../lib/utils";
import { Badge, Button, Card, CardTitle } from "./ui";

function dateLabel(value: string, language: string, bundled: string): string {
  if (!value) return bundled;
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : new Intl.DateTimeFormat(language, { dateStyle: "medium", timeStyle: "short" }).format(date);
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
  const { t, i18n } = useTranslation();
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
      setDiff(lines.join("\n\n") || t("views.scenarios.compare.empty"));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(false);
    }
  }, [toolId, left, right, t]);

  if (!active) return null;

  const options = [
    { value: "current", label: t("views.scenarios.compare.label.current") },
    ...scenarios.flatMap((scenario) => [
      {
        value: scenario.name,
        label: t("views.scenarios.compare.label.latest", { name: scenario.name }),
      },
      ...scenario.versions.map((version) => ({
        value: `${scenario.name}:${version.version}`,
        label:
          t("views.scenarios.compare.label.version", {
            name: scenario.name,
            version: version.version,
          }) + (version.label ? ` · ${version.label}` : ""),
      })),
    ]),
  ];

  return (
    <div className="space-y-5">
      <div className="rounded-lg border border-sky-100 bg-sky-50 px-3.5 py-2.5 text-2xs leading-relaxed text-sky-900">
        <Trans
          i18nKey="views.scenarios.guidance"
          components={{ strong: <span className="font-semibold" /> }}
        />
      </div>

      {error && (
        <div className="rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">{error}</div>
      )}

      <Card>
        <CardTitle
          title={t("views.scenarios.title")}
          subtitle={t("views.scenarios.active", { name: activeScenario })}
          action={<Badge tone="blue">{t("views.scenarios.count", { count: scenarios.length })}</Badge>}
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
                  {scenario.active && <Badge tone="green">{t("views.scenarios.badge.active")}</Badge>}
                  <span className="text-3xs text-slate-400">
                    {t("views.scenarios.version", { count: scenario.versions.length })}
                  </span>
                </div>
                {scenario.description && (
                  <p className="mt-0.5 text-2xs text-slate-500">{scenario.description}</p>
                )}
                <p className="mt-0.5 text-3xs text-slate-400">
                  {t("views.scenarios.updated", {
                    date: dateLabel(
                      scenario.updated_at || scenario.created_at,
                      i18n.language,
                      t("views.scenarios.bundled"),
                    ),
                  })}
                </p>
              </div>
              <div className="flex items-center gap-1.5">
                {!scenario.active && (
                  <Button
                    disabled={busy}
                    onClick={() => run(() => api.activateScenario(toolId, scenario.name))}
                  >
                    <RotateCcw className="h-3 w-3" /> {t("views.scenarios.activate")}
                  </Button>
                )}
                {scenario.name !== "base" && (
                  <Button
                    disabled={busy}
                    onClick={() => run(() => api.deleteScenario(toolId, scenario.name))}
                  >
                    <Trash2 className="h-3 w-3" /> {t("views.scenarios.delete")}
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap items-end gap-2 border-t border-slate-100 pt-4">
          <label className="min-w-[180px] flex-1">
            <span className="mb-1 block text-3xs font-semibold uppercase tracking-wider text-slate-500">
              {t("views.scenarios.new")}
            </span>
            <input
              className="form-control w-full"
              value={name}
              placeholder={t("views.scenarios.namePlaceholder")}
              onChange={(event) => setName(event.target.value)}
            />
          </label>
          <label className="min-w-[220px] flex-1">
            <span className="mb-1 block text-3xs font-semibold uppercase tracking-wider text-slate-500">
              {t("views.scenarios.description")}
            </span>
            <input
              className="form-control w-full"
              value={description}
              placeholder={t("views.scenarios.optional")}
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
            <Plus className="h-3 w-3" /> {t("views.scenarios.create")}
          </Button>
        </div>
      </Card>

      <Card>
        <CardTitle
          title={t("views.scenarios.history.title")}
          subtitle={t("views.scenarios.history.subtitle", { name: activeScenario })}
          action={
            <div className="flex items-center gap-2">
              <input
                className="form-control w-40"
                value={label}
                placeholder={t("views.scenarios.history.labelPlaceholder")}
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
                <Camera className="h-3 w-3" /> {t("views.scenarios.history.snapshot")}
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
                  {version.label || t("views.scenarios.history.automatic")}
                </span>
                <span className="text-3xs text-slate-400">
                  {dateLabel(version.created_at, i18n.language, t("views.scenarios.bundled"))}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500">{t("views.scenarios.history.empty")}</p>
        )}
      </Card>

      <Card>
        <CardTitle
          title={t("views.scenarios.compare.title")}
          subtitle={t("views.scenarios.compare.subtitle")}
        />
        <div className="flex flex-wrap items-end gap-2">
          <label className="min-w-[200px] flex-1">
            <span className="mb-1 block text-3xs font-semibold uppercase tracking-wider text-slate-500">
              {t("views.scenarios.compare.from")}
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
              {t("views.scenarios.compare.to")}
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
            <GitCompare className="h-3 w-3" /> {t("views.scenarios.compare.button")}
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
