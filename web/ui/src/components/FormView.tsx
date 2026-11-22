import { useEffect, useMemo, useRef, useState } from "react";
import { AlertCircle, Save } from "lucide-react";
import { api } from "../lib/api";
import type { Catalog, ModelFormat } from "../lib/types";
import { cn } from "../lib/utils";
import { applyDefaults, cleanDocument, SchemaForm, type Schema } from "./SchemaForm";
import { Button, EmptyState } from "./ui";

export function FormView({
  toolId,
  catalog,
  onSaved,
}: {
  toolId: string;
  catalog: Catalog;
  onSaved: () => void | Promise<void>;
}) {
  const [formats, setFormats] = useState<ModelFormat[]>([]);
  const [schemas, setSchemas] = useState<Record<string, string>>({});
  const [activeFile, setActiveFile] = useState("");
  const [document, setDocument] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const formatToolRef = useRef("");

  useEffect(() => {
    let cancelled = false;
    formatToolRef.current = "";
    setFormats([]);
    setSchemas({});
    setActiveFile("");
    setDocument(null);
    setError("");
    setNotice("");
    Promise.all([api.formats(toolId), api.schemas(toolId)])
      .then(([items, schemaMap]) => {
        if (cancelled) return;
        formatToolRef.current = toolId;
        setFormats(items);
        setSchemas(schemaMap);
        setActiveFile(items[0]?.file ?? "");
      })
      .catch((cause: unknown) => {
        if (!cancelled) setError(cause instanceof Error ? cause.message : String(cause));
      });
    return () => {
      cancelled = true;
    };
  }, [toolId]);

  const schema = useMemo<Schema | null>(() => {
    const format = formats.find((item) => item.file === activeFile);
    const raw = format ? schemas[format.schema] : undefined;
    if (!raw) return null;
    try {
      return JSON.parse(raw) as Schema;
    } catch {
      return null;
    }
  }, [formats, schemas, activeFile]);

  useEffect(() => {
    if (!activeFile || !schema || formatToolRef.current !== toolId) return;
    let cancelled = false;
    api
      .document(toolId, activeFile)
      .then((payload) => {
        if (!cancelled) setDocument(applyDefaults(payload.document, schema) as Record<string, unknown>);
      })
      .catch((cause: unknown) => {
        if (!cancelled) setError(cause instanceof Error ? cause.message : String(cause));
      });
    return () => {
      cancelled = true;
    };
  }, [toolId, activeFile, schema]);

  const save = async () => {
    if (!document || !schema) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const cleaned = cleanDocument(document, schema, true) as Record<string, unknown>;
      await api.saveDocument(toolId, activeFile, cleaned);
      setNotice(`${activeFile} saved. The YAML editor stays the source of truth.`);
      await onSaved();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-5">
      <p className="max-w-2xl text-2xs leading-relaxed text-slate-500">
        Fields suggest reusable values from your local reference catalog. You can still type any
        value required by the schema.
      </p>

      <div className="flex flex-wrap gap-2">
        {formats.map((format) => (
          <button
            key={format.file}
            onClick={() => {
              setActiveFile(format.file);
              setNotice("");
            }}
            className={cn(
              "content-button font-mono",
              format.file === activeFile
                ? "border-slate-900 bg-slate-900 text-white"
                : "border-slate-200 bg-white text-slate-500 hover:text-slate-800",
            )}
          >
            {format.file}
          </button>
        ))}
      </div>

      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-rose-50 px-3 py-2.5 text-xs text-rose-700">
          <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          {error}
        </div>
      )}
      {notice && <p className="rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-700">{notice}</p>}

      {schema && document ? (
        <>
          <SchemaForm schema={schema} value={document} catalog={catalog} onChange={setDocument} />
          <div className="flex justify-end">
            <Button variant="primary" loading={busy} onClick={() => void save()}>
              <Save className="h-3.5 w-3.5" />
              Save structured model
            </Button>
          </div>
        </>
      ) : (
        <EmptyState
          title="No editor for this file"
          hint="The JSON Schema for this model file could not be loaded. Use the YAML tab instead."
        />
      )}

    </div>
  );
}
