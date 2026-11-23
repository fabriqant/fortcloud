import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Check, ChevronDown, Pencil, Plus, Trash2, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import { api } from "../lib/api";
import type { Catalog } from "../lib/types";
import { cn } from "../lib/utils";
import { Button } from "./ui";

export function CatalogModal({
  catalog,
  onClose,
  onChange,
}: {
  catalog: Catalog;
  onClose: () => void;
  onChange: (catalog: Catalog) => void | Promise<void>;
}) {
  const { t } = useTranslation();
  const labelFor = (category: string): string =>
    t(`modals.catalog.category.${category}`, {
      defaultValue: category.charAt(0).toUpperCase() + category.slice(1),
    });
  const categories = Object.keys(catalog);
  const [openCategory, setOpenCategory] = useState(categories[0] ?? "");
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
        aria-label={t("modals.catalog.dialogLabel")}
        className="flex max-h-[85vh] w-full max-w-xl flex-col overflow-hidden rounded-xl bg-white shadow-2xl"
      >
        <header className="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">{t("modals.catalog.title")}</h2>
            <p className="mt-1 text-2xs leading-relaxed text-slate-500">
              {t("modals.catalog.descriptionStart")}{" "}
              <span className="font-mono text-slate-600">web/catalog.sqlite3</span>
              {t("modals.catalog.descriptionEnd")}
            </p>
          </div>
          <button
            onClick={onClose}
            aria-label={t("modals.catalog.close")}
            className="content-icon-button text-slate-400 hover:bg-slate-100 hover:text-slate-700"
          >
            <X className="h-4 w-4" />
          </button>
        </header>

        <div className="min-h-0 flex-1 overflow-y-auto p-3">
          <div className="space-y-2">
            {categories.map((category) => {
              const expanded = openCategory === category;
              const values = catalog[category] ?? [];
              return (
                <div key={category} className="overflow-hidden rounded-lg border border-slate-200">
                  <button
                    onClick={() => {
                      setOpenCategory(expanded ? "" : category);
                      setDraft("");
                      setEditing(null);
                      setError("");
                    }}
                    aria-expanded={expanded}
                    className="flex w-full items-center justify-between gap-3 px-4 py-2.5 text-left hover:bg-slate-50"
                  >
                    <span className="flex items-center gap-2 text-sm font-semibold text-slate-700">
                      <ChevronDown
                        className={cn(
                          "h-3.5 w-3.5 text-slate-400 transition-transform",
                          expanded ? "" : "-rotate-90",
                        )}
                      />
                      {labelFor(category)}
                    </span>
                    <span className="text-2xs text-slate-400">
                      {t("modals.catalog.values", { count: values.length })}
                    </span>
                  </button>

                  {expanded && (
                    <div className="space-y-3 border-t border-slate-200 bg-slate-50/60 p-4">
                      <div className="flex items-center gap-2">
                        <input
                          value={draft}
                          onChange={(event) => setDraft(event.target.value)}
                          onKeyDown={(event) => {
                            if (event.key === "Enter" && draft.trim()) {
                              event.preventDefault();
                              void run(() => api.addCatalogValue(category, draft.trim()), true);
                            }
                          }}
                          placeholder={t("modals.catalog.newValue", {
                            label: labelFor(category).toLowerCase(),
                          })}
                          className="form-control min-w-0 flex-1"
                        />
                        <Button
                          variant="primary"
                          loading={busy}
                          disabled={!draft.trim()}
                          onClick={() => void run(() => api.addCatalogValue(category, draft.trim()), true)}
                        >
                          <Plus className="h-3.5 w-3.5" />
                          {t("modals.catalog.add")}
                        </Button>
                      </div>

                      {error && (
                        <p className="rounded-md bg-rose-50 px-3 py-2 text-2xs text-rose-700">{error}</p>
                      )}

                      <div className="grid gap-1.5 sm:grid-cols-2">
                        {values.map((value) => (
                          <div
                            key={value}
                            className="group flex items-center gap-2 rounded-md border border-slate-200 bg-white px-2.5 py-2"
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
                                        () => api.renameCatalogValue(category, value, edited.trim()),
                                        true,
                                      );
                                    }
                                    if (event.key === "Escape") setEditing(null);
                                  }}
                                  className="form-control min-w-0 flex-1"
                                />
                                <button
                                  aria-label={t("modals.catalog.save", { value })}
                                  disabled={busy || !edited.trim()}
                                  onClick={() =>
                                    void run(
                                      () => api.renameCatalogValue(category, value, edited.trim()),
                                      true,
                                    )
                                  }
                                  className="content-icon-button text-emerald-600 hover:bg-emerald-50 hover:text-emerald-700 disabled:opacity-40"
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
                                  aria-label={t("modals.catalog.edit", { value })}
                                  onClick={() => {
                                    setEditing(value);
                                    setEdited(value);
                                  }}
                                  className="content-icon-button text-slate-400 opacity-60 hover:bg-slate-100 hover:text-slate-700 group-hover:opacity-100"
                                >
                                  <Pencil className="h-3.5 w-3.5" />
                                </button>
                                <button
                                  aria-label={t("modals.catalog.remove", { value })}
                                  disabled={busy}
                                  onClick={() => void run(() => api.removeCatalogValue(category, value))}
                                  className="content-icon-button text-slate-400 opacity-60 hover:bg-rose-50 hover:text-rose-600 group-hover:opacity-100"
                                >
                                  <Trash2 className="h-3.5 w-3.5" />
                                </button>
                              </>
                            )}
                          </div>
                        ))}
                        {!values.length && (
                          <p className="text-2xs text-slate-400">{t("modals.catalog.empty")}</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <footer className="flex items-center justify-between border-t border-slate-200 px-5 py-3 text-footer text-slate-400">
          <span>{t("modals.catalog.footerNote")}</span>
          <Button variant="ghost" onClick={onClose}>
            {t("modals.done")}
          </Button>
        </footer>
      </div>
    </div>,
    document.body,
  );
}
