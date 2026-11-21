import { useCallback, useEffect, useState } from "react";
import { CheckCircle2, FileUp, ShieldCheck, Trash2 } from "lucide-react";
import { api } from "../lib/api";
import type { ImportDiff, ImportInfo } from "../lib/types";
import { cn } from "../lib/utils";
import { Button, Card, CardTitle, EmptyState } from "./ui";

function diffTone(line: string) {
  if (line.startsWith("+") && !line.startsWith("+++")) return "bg-emerald-50 text-emerald-800";
  if (line.startsWith("-") && !line.startsWith("---")) return "bg-rose-50 text-rose-800";
  if (line.startsWith("@@")) return "bg-sky-50 text-sky-700";
  return "text-slate-500";
}

export function ImportView({
  toolId,
  files,
  onAccepted,
}: {
  toolId: string;
  files: string[];
  onAccepted: () => void | Promise<void>;
}) {
  const [target, setTarget] = useState("");
  const [content, setContent] = useState("");
  const [staged, setStaged] = useState<ImportInfo[]>([]);
  const [selected, setSelected] = useState("");
  const [diff, setDiff] = useState<ImportDiff | null>(null);
  const [busy, setBusy] = useState<"stage" | "accept" | "discard" | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    setTarget(files[0] ?? "");
    setContent("");
    setSelected("");
    setDiff(null);
    setNotice("");
    setError("");
  }, [toolId, files]);

  const refreshStaged = useCallback(async () => {
    const items = await api.imports(toolId);
    setStaged(items);
    setSelected((current) =>
      items.some((item) => item.name === current) ? current : items[0]?.name ?? "",
    );
  }, [toolId]);

  useEffect(() => {
    void refreshStaged().catch((cause: unknown) =>
      setError(cause instanceof Error ? cause.message : String(cause)),
    );
  }, [refreshStaged, toolId]);

  useEffect(() => {
    if (!selected) {
      setDiff(null);
      return;
    }
    let cancelled = false;
    api
      .importDiff(toolId, selected)
      .then((payload) => {
        if (!cancelled) setDiff(payload);
      })
      .catch(() => {
        if (!cancelled) setDiff(null);
      });
    return () => {
      cancelled = true;
    };
  }, [toolId, selected, staged]);

  const stage = async () => {
    if (!target || !content.trim()) return;
    setBusy("stage");
    setError("");
    setNotice("");
    try {
      await api.stageImport(toolId, target, content);
      setContent("");
      await refreshStaged();
      setSelected(target);
      setNotice(`${target} staged. Review the diff before accepting it.`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(null);
    }
  };

  const accept = async () => {
    if (!selected) return;
    setBusy("accept");
    setError("");
    try {
      await api.acceptImport(toolId, selected);
      await refreshStaged();
      setDiff(null);
      setNotice(`${selected} applied to the workspace model. Run Check to regenerate artifacts.`);
      await onAccepted();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(null);
    }
  };

  const discard = async () => {
    if (!selected) return;
    setBusy("discard");
    setError("");
    try {
      await api.discardImport(toolId, selected);
      await refreshStaged();
      setDiff(null);
      setNotice(`${selected} discarded.`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(null);
    }
  };

  const readFile = async (file: File | undefined) => {
    if (!file) return;
    const text = await file.text();
    setContent(text);
    if (files.includes(file.name)) setTarget(file.name);
    setError("");
    setNotice("");
  };

  return (
    <div className="space-y-5">
      <div className="flex items-start gap-2 rounded-lg border border-sky-100 bg-sky-50 px-3.5 py-2.5 text-[11px] leading-relaxed text-sky-900">
        <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0" />
        <div>
          <p>
            Imports are never applied automatically. Stage YAML, review the diff, then accept it.
            The console never receives cloud credentials.
          </p>
          <p className="mt-1.5 font-mono text-[10px] text-sky-800">
            Local AWS connector: python -m connectors.aws --profile &lt;profile&gt; --region &lt;region&gt;
          </p>
        </div>
      </div>

      {error && <p className="rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">{error}</p>}
      {notice && <p className="rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-700">{notice}</p>}

      <Card>
        <CardTitle
          title="Stage a YAML proposal"
          subtitle="Paste YAML or pick a file. The target must match one of this tool's model files."
        />
        <div className="grid gap-4 lg:grid-cols-[220px_minmax(0,1fr)]">
          <div className="space-y-3">
            <label className="block">
              <span className="mb-1.5 block text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Target file
              </span>
              <select
                value={target}
                onChange={(event) => setTarget(event.target.value)}
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 font-mono text-[11px] text-slate-700 outline-none focus:border-slate-400"
              >
                {files.map((file) => (
                  <option key={file} value={file}>
                    {file}
                  </option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="mb-1.5 block text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Or upload
              </span>
              <span className="flex cursor-pointer items-center gap-2 rounded-lg border border-dashed border-slate-300 px-3 py-2 text-[11px] text-slate-500 hover:border-slate-400 hover:text-slate-700">
                <FileUp className="h-3.5 w-3.5" />
                Choose a YAML file
                <input
                  type="file"
                  accept=".yaml,.yml,.json,text/plain"
                  className="hidden"
                  onChange={(event) => void readFile(event.target.files?.[0])}
                />
              </span>
            </label>
          </div>
          <div>
            <span className="mb-1.5 block text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              Proposed content
            </span>
            <textarea
              value={content}
              onChange={(event) => setContent(event.target.value)}
              spellCheck={false}
              placeholder={"version: 1\ncomponents:\n  - id: ..."}
              className="h-56 w-full resize-y rounded-lg border border-slate-200 bg-slate-950 p-3 font-mono text-[11px] leading-relaxed text-slate-200 outline-none placeholder:text-slate-600 focus:border-slate-500"
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <Button variant="primary" loading={busy === "stage"} disabled={!target || !content.trim()} onClick={() => void stage()}>
            Stage proposal
          </Button>
        </div>
      </Card>

      <div className="grid gap-5 lg:grid-cols-[210px_minmax(0,1fr)]">
        <Card padded={false} className="overflow-hidden">
          <div className="border-b border-slate-200 px-4 py-3">
            <p className="text-xs font-semibold text-slate-800">Staged proposals</p>
            <p className="mt-0.5 text-[10px] text-slate-400">{staged.length} waiting for review</p>
          </div>
          <div className="space-y-1 p-2">
            {staged.length ? (
              staged.map((item) => (
                <button
                  key={item.name}
                  onClick={() => setSelected(item.name)}
                  className={cn(
                    "w-full rounded-md px-2.5 py-2 text-left font-mono text-[11px] transition",
                    item.name === selected
                      ? "bg-slate-900 text-white"
                      : "text-slate-600 hover:bg-slate-100",
                  )}
                >
                  <span className="block truncate">{item.name}</span>
                  <span className={cn("block text-[9px]", item.name === selected ? "text-slate-400" : "text-slate-400")}>
                    {item.size} bytes
                  </span>
                </button>
              ))
            ) : (
              <p className="px-2.5 py-3 text-[11px] leading-relaxed text-slate-400">
                No proposal staged. Paste YAML above or run a local connector.
              </p>
            )}
          </div>
        </Card>

        <Card>
          <CardTitle
            title={diff ? `Diff · ${diff.file}` : "Diff"}
            subtitle={diff ? (diff.changed ? "Review every line before accepting." : "No changes.") : undefined}
            action={
              diff && (
                <div className="flex gap-2">
                  <Button loading={busy === "discard"} disabled={!selected} onClick={() => void discard()}>
                    <Trash2 className="h-3.5 w-3.5" />
                    Discard
                  </Button>
                  <Button
                    variant="primary"
                    loading={busy === "accept"}
                    disabled={!selected || !diff.changed}
                    onClick={() => void accept()}
                  >
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Accept
                  </Button>
                </div>
              )
            }
          />
          {diff ? (
            <pre className="max-h-[440px] overflow-auto rounded-lg bg-slate-950 p-4 font-mono text-[11px] leading-relaxed">
              {diff.diff.split("\n").map((line, index) => (
                <div key={index} className={cn("px-1", diffTone(line))}>
                  {line || " "}
                </div>
              ))}
            </pre>
          ) : (
            <EmptyState title="No diff to show" hint="Stage a proposal to compare it with the current model." />
          )}
        </Card>
      </div>
    </div>
  );
}
