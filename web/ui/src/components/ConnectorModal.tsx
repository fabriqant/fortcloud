import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { AlertCircle, CheckCircle2, Cloud, Play, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import type { ConnectorInfo, ConnectorRunResult } from "../lib/types";
import { cn } from "../lib/utils";
import { Button } from "./ui";

function installCommand(provider: ConnectorInfo): string | null {
  const requirements: Record<string, string> = {
    aws: "aws",
    azure: "azure",
    gcp: "gcp",
  };
  const suffix = requirements[provider.id];
  return suffix ? `python -m pip install -r web/connectors/requirements-${suffix}.txt` : null;
}

export function ConnectorModal({
  onClose,
  onOpenImport,
}: {
  onClose: () => void;
  onOpenImport: () => void;
}) {
  const { t } = useTranslation();
  const [providers, setProviders] = useState<ConnectorInfo[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [values, setValues] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ConnectorRunResult | null>(null);

  const selected = providers.find((provider) => provider.id === selectedId) ?? providers[0] ?? null;

  useEffect(() => {
    api
      .connectors()
      .then((items) => {
        setProviders(items);
        setSelectedId(items[0]?.id ?? "");
        const defaults: Record<string, string> = {};
        items[0]?.fields.forEach((field) => {
          defaults[field.name] = field.default ?? field.identifiers[0] ?? "";
        });
        setValues(defaults);
      })
      .catch((cause: unknown) => setError(String(cause)));
  }, []);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  const choose = (provider: ConnectorInfo) => {
    setSelectedId(provider.id);
    setResult(null);
    setError("");
    const next: Record<string, string> = {};
    provider.fields.forEach((field) => {
      next[field.name] = field.default ?? field.identifiers[0] ?? "";
    });
    setValues(next);
  };

  const run = async () => {
    if (!selected) return;
    const payload: Record<string, string> = { provider: selected.id };
    selected.fields.forEach((field) => {
      const value = values[field.name]?.trim();
      if (value) payload[field.name] = value;
    });
    setBusy(true);
    setError("");
    setResult(null);
    try {
      setResult(await api.runConnector(payload));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(false);
    }
  };

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={t("modals.connector.title")}
        className="flex max-h-[88vh] w-full max-w-2xl flex-col overflow-hidden rounded-xl bg-white shadow-2xl"
      >
        <header className="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-4">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-white">
              <Cloud className="h-4 w-4" />
            </span>
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                {t("modals.connector.title")}
              </h2>
              <p className="mt-1 max-w-xl text-2xs leading-relaxed text-slate-500">
                {t("modals.connector.description")}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label={t("modals.connector.close")}
            className="content-icon-button text-slate-400 hover:bg-slate-100 hover:text-slate-700"
          >
            <X className="h-4 w-4" />
          </button>
        </header>

        <div className="min-h-0 flex-1 overflow-y-auto p-5">
          <div className="flex flex-wrap gap-2">
            {providers.map((provider) => (
              <button
                key={provider.id}
                onClick={() => choose(provider)}
                className={cn(
                  "content-button px-3 py-2 text-xs font-semibold",
                  selected?.id === provider.id
                    ? "border-slate-900 bg-slate-900 text-white"
                    : "border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900",
                )}
              >
                {provider.label}
                {!provider.installed && <span className="ml-1 text-amber-400">•</span>}
              </button>
            ))}
          </div>

          {selected ? (
            <div className="mt-5 space-y-4">
              <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-4">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-sm font-semibold text-slate-800">{selected.label}</h3>
                  <span
                    className={cn(
                      "text-2xs font-semibold",
                      selected.installed ? "text-emerald-600" : "text-amber-600",
                    )}
                  >
                    {selected.installed
                      ? t("modals.connector.sdkAvailable")
                      : t("modals.connector.sdkMissing")}
                  </span>
                </div>
                <p className="mt-1 text-2xs leading-relaxed text-slate-500">{selected.description}</p>
                {!selected.installed && installCommand(selected) && (
                  <code className="mt-3 block break-all rounded bg-white px-2.5 py-2 font-mono text-2xs text-slate-700">
                    {installCommand(selected)}
                  </code>
                )}
              </div>

              <div className="space-y-3">
                {selected.fields.map((field) => (
                  <div key={field.name}>
                    <label className="mb-1 block text-2xs font-semibold text-slate-600">
                      {field.label}
                      {field.required && <span className="ml-1 text-rose-500">*</span>}
                    </label>
                    <input
                      className="form-control w-full"
                      value={values[field.name] ?? ""}
                      placeholder={field.placeholder}
                      list={`connector-${selected.id}-${field.name}`}
                      onChange={(event) =>
                        setValues((current) => ({ ...current, [field.name]: event.target.value }))
                      }
                    />
                    <datalist id={`connector-${selected.id}-${field.name}`}>
                      {field.identifiers.map((identifier) => (
                        <option key={identifier} value={identifier} />
                      ))}
                    </datalist>
                    {field.help && (
                      <p className="mt-1 text-2xs text-slate-400">{field.help}</p>
                    )}
                  </div>
                ))}
              </div>

              <p className="rounded-md bg-slate-50 px-3 py-2 text-2xs leading-relaxed text-slate-500">
                {t("modals.connector.guidanceStart")}{" "}
                <span className="font-mono">components.yaml</span>{" "}
                {t("modals.connector.guidanceMiddle")}{" "}
                <span className="font-semibold">{t("modals.connector.reviewLabel")}</span>{" "}
                {t("modals.connector.guidanceEnd")}
              </p>

              <Button variant="primary" loading={busy} onClick={() => void run()}>
                <Play className="h-3.5 w-3.5" />
                {t("modals.connector.run")}
              </Button>

              {error && (
                <div className="flex items-start gap-2 rounded-md bg-rose-50 px-3 py-2 text-2xs text-rose-700">
                  <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                  <span className="whitespace-pre-wrap break-words">{error}</span>
                </div>
              )}

              {result && (
                <div className="space-y-2 rounded-lg border border-emerald-200 bg-emerald-50/60 p-3">
                  <div className="flex items-center gap-2 text-xs font-semibold text-emerald-800">
                    <CheckCircle2 className="h-4 w-4" />
                    {t("modals.connector.staged", { label: selected.label })}
                  </div>
                  <code className="block break-all font-mono text-2xs text-emerald-900/80">
                    {result.command}
                  </code>
                  {result.output && (
                    <pre className="max-h-24 overflow-auto whitespace-pre-wrap font-mono text-2xs text-emerald-900/70">
                      {result.output}
                    </pre>
                  )}
                  <Button variant="secondary" onClick={onOpenImport}>
                    {t("modals.connector.review")}
                  </Button>
                </div>
              )}
            </div>
          ) : (
            <p className="mt-5 text-2xs text-slate-500">{t("modals.connector.loading")}</p>
          )}
        </div>

        <footer className="flex items-center justify-between border-t border-slate-200 px-5 py-3 text-footer text-slate-400">
          <span>{t("modals.connector.footer")}</span>
          <Button variant="ghost" onClick={onClose}>
            {t("modals.done")}
          </Button>
        </footer>
      </div>
    </div>,
    document.body,
  );
}
