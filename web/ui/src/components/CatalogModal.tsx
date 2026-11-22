import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Check, Pencil, Plus, Trash2, X } from "lucide-react";
import { api } from "../lib/api";
import type { Catalog } from "../lib/types";
import { cn } from "../lib/utils";
import { Button } from "./ui";

function labelFor(category: string): string {
  return category.charAt(0).toUpperCase() + category.slice(1);
}

export function CatalogModal({
  catalog,
  onClose,
  onChange,
}: {
  catalog: Catalog;
  onClose: () => void;
  onChange: (catalog: Catalog) => void | Promise<void>;
}) {
  const categories = Object.keys(catalog);
  const [active, setActive] = useState(categories[0] ?? "");
  const [draft, setDraft] = useState("");
  const [editing, setEditing] = useState<string | null>(null);
  const [edited, setEdited] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  const values = catalog[active] ?? [];

  const run = async (action: () => Promise<unknown>, reset = false) => {
    setBusy(true);
    setError("");
    try {
      await action();
      await onChange(await api.catalog());
      if (reset) {
        setDraft("");
        setEditing(null);
      }
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
        aria-label="Reference data catalog"
        className="flex max-h-[85vh] w-full max-w-3xl flex-col overflow-hidden rounded-xl bg-white shadow-2xl"
      >
        <header className="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">Reference data</h2>
            <p className="mt-1 text-2xs leading-relaxed text-slate-500">
              Reusable values suggested in guided forms. Stored locally in{" "}
              <span className="font-mono text-slate-600">web/catalog.sqlite3</span>. You can always
              type a different value in a form.
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close reference data"
            className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
          >
            <X className="h-4 w-4" />
          </button>
        </header>

        <div className="flex min-h-0 flex-1">
          <nav className="w-44 shrink-0 space-y-0.5 overflow-y-auto border-r border-slate-200 bg-slate-50 p-3">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => {
                  setActive(category);
                  setEditing(null);
                  setError("");
                }}
                className={cn(
                  "flex w-full items-center justify-between rounded-md px-2.5 py-2 text-left text-control font-semibold transition",
                  category === active
                    ? "bg-slate-900 text-white"
                    : "text-slate-500 hover:bg-white hover:text-slate-800",
                )}
              >
                {labelFor(category)}
                <span className={category === active ? "text-slate-400" : "text-slate-400"}>
                  {catalog[category]?.length ?? 0}
                </span>
              </button>
            ))}
          </nav>

          <div className="min-w-0 flex-1 overflow-y-auto p-5">
            <div className="mb-4 flex items-center gap-2">
              <input
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && draft.trim()) {
                    event.preventDefault();
                    void run(() => api.addCatalogValue(active, draft.trim()), true);
                  }
                }}
                placeholder={`New ${labelFor(active).toLowerCase()} value`}
                className="min-w-0 flex-1 rounded-md border border-slate-200 px-2.5 py-2 text-control outline-none focus:border-slate-400"
              />
              <Button
                variant="primary"
                loading={busy}
                disabled={!draft.trim()}
                onClick={() => void run(() => api.addCatalogValue(active, draft.trim()), true)}
              >
                <Plus className="h-3.5 w-3.5" />
                Add
              </Button>
            </div>

            {error && <p className="mb-3 rounded-md bg-rose-50 px-3 py-2 text-2xs text-rose-700">{error}</p>}

            <div className="grid gap-1.5 sm:grid-cols-2">
              {values.map((value) => (
                <div
                  key={value}
                  className="group flex items-center gap-2 rounded-md border border-slate-200 bg-slate-50/70 px-2.5 py-2"
                >
                  {editing === value ? (
                    <>
                      <input
                        autoFocus
                        value={edited}
                        onChange={(event) => setEdited(event.target.value)}
                        onKeyDown={(event) => {
                          if (event.key === "Enter" && edited.trim()) {
                            event.preventDefault();
                            void run(
                              () => api.renameCatalogValue(active, value, edited.trim()),
                              true,
                            );
                          }
                          if (event.key === "Escape") setEditing(null);
                        }}
                        className="min-w-0 flex-1 rounded border border-slate-300 bg-white px-1.5 py-1 text-control outline-none focus:border-slate-500"
                      />
                      <button
                        aria-label={`Save ${value}`}
                        disabled={busy || !edited.trim()}
                        onClick={() =>
                          void run(() => api.renameCatalogValue(active, value, edited.trim()), true)
                        }
                        className="text-emerald-600 hover:text-emerald-700 disabled:opacity-40"
                      >
                        <Check className="h-3.5 w-3.5" />
                      </button>
                    </>
                  ) : (
                    <>
                      <span className="min-w-0 flex-1 truncate font-mono text-control text-slate-700">
                        {value}
                      </span>
                      <button
                        aria-label={`Edit ${value}`}
                        onClick={() => {
                          setEditing(value);
                          setEdited(value);
                        }}
                        className="text-slate-400 opacity-60 hover:text-slate-700 group-hover:opacity-100"
                      >
                        <Pencil className="h-3.5 w-3.5" />
                      </button>
                      <button
                        aria-label={`Remove ${value}`}
                        disabled={busy}
                        onClick={() => void run(() => api.removeCatalogValue(active, value))}
                        className="text-slate-400 opacity-60 hover:text-rose-600 group-hover:opacity-100"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </>
                  )}
                </div>
              ))}
              {!values.length && (
                <p className="text-2xs text-slate-400">No values in this category yet.</p>
              )}
            </div>
          </div>
        </div>

        <footer className="flex items-center justify-between border-t border-slate-200 px-5 py-3 text-footer text-slate-400">
          <span>Defaults are restored only when the database is deleted.</span>
          <Button variant="ghost" onClick={onClose}>
            Done
          </Button>
        </footer>
      </div>
    </div>,
    document.body,
  );
}
