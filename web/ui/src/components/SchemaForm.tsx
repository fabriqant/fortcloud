import { useEffect, useRef, useState } from "react";
import { ChevronDown, Plus, Trash2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { Catalog } from "../lib/types";
import { cn } from "../lib/utils";

type TFunc = ReturnType<typeof useTranslation>["t"];

export interface Schema {
  type?: string | string[];
  title?: string;
  enum?: unknown[];
  const?: unknown;
  properties?: Record<string, Schema>;
  required?: string[];
  items?: Schema;
  minimum?: number;
  maximum?: number;
  minLength?: number;
  pattern?: string;
  oneOf?: Schema[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function schemaType(schema: Schema): string {
  if (Array.isArray(schema.type)) return schema.type.find((item) => item !== "null") ?? "string";
  if (schema.type) return schema.type;
  if (schema.enum || schema.const !== undefined) return "string";
  if (schema.properties) return "object";
  if (schema.items) return "array";
  return "string";
}

function allowsNull(schema: Schema): boolean {
  return Array.isArray(schema.type) && schema.type.includes("null");
}

function labelFor(name: string, t: TFunc): string {
  const fallback = name.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
  return t(`forms.field.${name}`, { defaultValue: fallback });
}

const SUGGESTION_CATEGORIES: Record<string, string> = {
  owner: "owners",
  owners: "owners",
  team: "teams",
  teams: "teams",
  escalation: "teams",
  person: "people",
  people: "people",
  participant: "participants",
  participants: "participants",
  service: "services",
  services: "services",
  component: "components",
  components: "components",
  target: "components",
  system: "components",
  primary: "components",
  standby: "components",
  from: "components",
  to: "components",
  pair: "pairs",
  pairs: "pairs",
  provider: "providers",
  providers: "providers",
  region: "regions",
  regions: "regions",
  zone: "zones",
  zones: "zones",
  environment: "environments",
  environments: "environments",
  role: "roles",
  roles: "roles",
  audience: "audiences",
  audiences: "audiences",
  strategy: "strategies",
  strategies: "strategies",
  scenario: "scenarios",
  scenarios: "scenarios",
  channel: "channels",
  channels: "channels",
  notify: "channels",
  stakeholder: "stakeholders",
  stakeholders: "stakeholders",
  contact: "stakeholders",
  asset: "assets",
  assets: "assets",
  backup: "backups",
  backups: "backups",
  restore: "restores",
  restores: "restores",
  dependency: "dependencies",
  dependencies: "dependencies",
  flow: "flows",
  flows: "flows",
  risk: "risks",
  risks: "risks",
  check: "checks",
  checks: "checks",
  objective: "objectives",
  objectives: "objectives",
  signal: "signals",
  signals: "signals",
  sink: "sinks",
  sinks: "sinks",
  metric: "metrics",
  metrics: "metrics",
  operation: "operations",
  operations: "operations",
  pipeline: "pipelines",
  pipelines: "pipelines",
  secret: "secrets",
  secrets: "secrets",
  principal: "principals",
  principals: "principals",
  permission: "permissions",
  permissions: "permissions",
  grant: "permissions",
  grants: "permissions",
  runbook: "runbooks",
  runbooks: "runbooks",
  drill: "drills",
  drills: "drills",
  signoff: "signoffs",
  signoffs: "signoffs",
  approval: "signoffs",
  approved_by: "signoffs",
  assignment: "assignments",
  assignments: "assignments",
  action: "actions",
  actions: "actions",
  mitigation: "actions",
  mitigations: "actions",
  steps: "actions",
};

function suggestionsFor(name: string, catalog?: Catalog): string[] {
  const key = name.replace(/-\d+$/, "").toLowerCase();
  const category = SUGGESTION_CATEGORIES[key];
  return category ? catalog?.[category] ?? [] : [];
}

const TITLE_KEYS = [
  "name",
  "id",
  "service",
  "component",
  "asset",
  "primary",
  "standby",
  "scenario",
  "metric",
  "channel",
  "principal",
  "strategy",
  "role",
  "person",
];

function itemTitle(item: unknown, index: number, t: TFunc): string {
  const fallback = () => t("forms.schema.item", { index: index + 1 });
  if (isRecord(item)) {
    for (const key of TITLE_KEYS) {
      const candidate = item[key];
      if (typeof candidate === "string" && candidate.trim()) return candidate.trim();
      if (typeof candidate === "number") return String(candidate);
    }
    const candidate = Object.values(item).find(
      (value) => typeof value === "string" && value.trim(),
    );
    if (typeof candidate === "string" && candidate.trim()) return candidate.trim();
    return fallback();
  }
  if (item === undefined || item === null || item === "") return fallback();
  return String(item);
}

function blankFor(schema: Schema): unknown {
  const type = schemaType(schema);
  if (schema.const !== undefined) return schema.const;
  if (schema.enum?.length) return schema.enum[0];
  if (type === "object") return {};
  if (type === "array") return [];
  if (type === "boolean") return false;
  if (type === "integer" || type === "number") return 0;
  return "";
}

export function applyDefaults(value: unknown, schema: Schema): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => applyDefaults(item, schema.items ?? {}));
  }
  if (!isRecord(value)) return isRecord(schema.properties) ? {} : value;
  const result: Record<string, unknown> = { ...value };
  for (const [key, child] of Object.entries(schema.properties ?? {})) {
    result[key] = result[key] === undefined ? blankFor(child) : applyDefaults(result[key], child);
  }
  return result;
}

export function cleanDocument(value: unknown, schema: Schema, required = false): unknown {
  if (Array.isArray(value)) {
    const items = value
      .map((item) => cleanDocument(item, schema.items ?? {}, true))
      .filter((item) => item !== undefined);
    return items.length || required ? items : undefined;
  }
  if (isRecord(value)) {
    const result: Record<string, unknown> = {};
    for (const [key, child] of Object.entries(schema.properties ?? {})) {
      const childRequired = (schema.required ?? []).includes(key);
      const cleaned = cleanDocument(value[key], child, childRequired);
      if (cleaned !== undefined) result[key] = cleaned;
    }
    return Object.keys(result).length || required ? result : undefined;
  }
  if (value === undefined || value === null || value === "") {
    if (allowsNull(schema)) return null;
    return required ? "" : undefined;
  }
  return value;
}

function PrimitiveField({
  name,
  schema,
  value,
  required,
  suggestions = [],
  compact = false,
  onChange,
}: {
  name: string;
  schema: Schema;
  value: unknown;
  required: boolean;
  suggestions?: string[];
  compact?: boolean;
  onChange: (value: unknown) => void;
}) {
  const { t } = useTranslation();
  const type = schemaType(schema);
  const label = schema.title ?? labelFor(name, t);
  const inputClass = "form-control";
  const [customOpen, setCustomOpen] = useState(false);

  if (allowsNull(schema) && value === null) {
    return (
      <label className={cn("block", compact && "min-w-0")}>
        {compact ? (
          <span className="sr-only">{label}</span>
        ) : (
          <span className="mb-1 block text-3xs font-semibold text-slate-500">
            {label} <span className="font-normal text-slate-400">· {t("forms.schema.null")}</span>
          </span>
        )}
        <button
          type="button"
          onClick={() => onChange(blankFor(schema))}
          className={cn("w-full", inputClass, "text-left text-slate-400 hover:border-slate-400")}
        >
          {t("forms.schema.setValue")}
        </button>
      </label>
    );
  }

  const current = value === undefined || value === null ? "" : String(value);
  const options = suggestions.filter((option, index) => suggestions.indexOf(option) === index);
  const customActive = customOpen || (current !== "" && !options.includes(current));

  let control;
  if (schema.enum) {
    control = (
      <select
        className={cn(inputClass, "w-full")}
        value={String(value ?? "")}
        onChange={(event) => onChange(event.target.value)}
      >
        {!required && <option value="">—</option>}
        {schema.enum.map((option) => (
          <option key={String(option)} value={String(option)}>
            {String(option)}
          </option>
        ))}
      </select>
    );
  } else if (schema.const !== undefined) {
    control = (
      <input className={cn(inputClass, "w-14 bg-slate-50 text-slate-500")} value={String(schema.const)} disabled />
    );
  } else if (type === "boolean") {
    control = (
      <label className="flex items-center gap-2 pt-1 text-control text-slate-600">
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(event) => onChange(event.target.checked)}
          className="h-3.5 w-3.5 rounded border-slate-300"
        />
        {t("forms.schema.enabled")}
      </label>
    );
  } else if (type === "integer" || type === "number") {
    control = (
      <input
        type="number"
        className={cn(inputClass, "w-full")}
        value={current}
        min={schema.minimum}
        max={schema.maximum}
        onChange={(event) => onChange(event.target.value === "" ? "" : Number(event.target.value))}
      />
    );
  } else if (options.length) {
    control = (
      <div>
        <select
          className={cn(inputClass, "w-full")}
          value={customActive ? "__custom__" : current}
          onChange={(event) => {
            if (event.target.value === "__custom__") {
              setCustomOpen(true);
              return;
            }
            setCustomOpen(false);
            onChange(event.target.value);
          }}
        >
          {!required && <option value="">—</option>}
          {options.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
          <option value="__custom__">{t("forms.schema.customOption")}</option>
        </select>
        {customActive && (
          <input
            type="text"
            className={cn(inputClass, "mt-1.5 w-full")}
            value={current}
            placeholder={t("forms.schema.customValue")}
            onChange={(event) => onChange(event.target.value)}
          />
        )}
      </div>
    );
  } else {
    control = (
      <input
        type="text"
        className={cn(inputClass, "w-full")}
        value={current}
        placeholder={schema.pattern ? t("forms.schema.pattern") : undefined}
        onChange={(event) => onChange(event.target.value)}
      />
    );
  }

  return (
    <label className={cn("block", compact && "min-w-0")}>
      {compact ? (
        <span className="sr-only">
          {label} {required && "*"}
        </span>
      ) : (
        <span className="mb-1 block text-3xs font-semibold text-slate-500">
          {label} {required && <span className="text-rose-400">*</span>}
        </span>
      )}
      {control}
    </label>
  );
}

function ArrayField({
  name,
  schema,
  value,
  catalog,
  onChange,
}: {
  name: string;
  schema: Schema;
  value: unknown;
  catalog?: Catalog;
  onChange: (value: unknown) => void;
}) {
  const { t } = useTranslation();
  const items = Array.isArray(value) ? value : [];
  const itemSchema = schema.items ?? {};
  const objectItems = schemaType(itemSchema) === "object";
  const label = schema.title ?? labelFor(name, t);

  // Stable keys keep the enter/leave animation on the right row after removals.
  const idsRef = useRef<number[]>([]);
  const nextIdRef = useRef(0);
  while (idsRef.current.length < items.length) idsRef.current.push(nextIdRef.current++);
  if (idsRef.current.length > items.length) idsRef.current = idsRef.current.slice(0, items.length);
  const ids = idsRef.current;

  const [open, setOpen] = useState<Record<number, boolean>>({});
  const [entering, setEntering] = useState<Record<number, boolean>>({});
  const [exiting, setExiting] = useState<Record<number, boolean>>({});
  const itemsRef = useRef(items);
  itemsRef.current = items;
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    const doomed = new Set(
      Object.entries(exiting)
        .filter(([, active]) => active)
        .map(([id]) => Number(id)),
    );
    if (!doomed.size) return;
    const timer = window.setTimeout(() => {
      const currentItems = itemsRef.current;
      const currentIds = idsRef.current;
      const nextItems = currentItems.filter((_, index) => !doomed.has(currentIds[index]));
      idsRef.current = currentIds.filter((id) => !doomed.has(id));
      setOpen((previous) => {
        const next = { ...previous };
        doomed.forEach((id) => delete next[id]);
        return next;
      });
      setExiting((previous) => {
        const next = { ...previous };
        doomed.forEach((id) => delete next[id]);
        return next;
      });
      onChangeRef.current(nextItems);
    }, 220);
    return () => window.clearTimeout(timer);
  }, [exiting]);

  useEffect(() => {
    if (!Object.values(entering).some(Boolean)) return;
    const timer = window.setTimeout(() => setEntering({}), 280);
    return () => window.clearTimeout(timer);
  }, [entering]);

  const setItem = (index: number, next: unknown) => {
    const copy = [...items];
    copy[index] = next;
    onChange(copy);
  };

  const add = () => {
    const id = nextIdRef.current++;
    idsRef.current = [...ids, id];
    setEntering((previous) => ({ ...previous, [id]: true }));
    onChange([...items, blankFor(itemSchema)]);
  };

  const remove = (id: number) => {
    setExiting((previous) => ({ ...previous, [id]: true }));
  };

  const animationProps = (id: number) => ({
    "data-entering": entering[id] === true ? "true" : undefined,
    "data-exiting": exiting[id] === true ? "true" : undefined,
  });

  return (
    <div className="sm:col-span-2">
      <div className="flex items-center justify-between gap-2 border-b border-slate-200 pb-1.5">
        <p className="text-3xs font-semibold uppercase tracking-wider text-slate-400">
          {label} <span className="text-slate-300">· {items.length}</span>
        </p>
        <button
          type="button"
          onClick={add}
          className="content-button border-slate-200 bg-white text-slate-600 hover:border-slate-400"
        >
          <Plus className="h-3 w-3" /> {t("forms.schema.add")}
        </button>
      </div>

      <div className={cn("grid gap-3 pt-1", objectItems ? "grid-cols-1" : "grid-cols-3")}>
        {items.map((item, index) => {
          const id = ids[index];

          if (!objectItems) {
            return (
              <div
                key={id}
                {...animationProps(id)}
                className="array-item flex min-w-0 items-start gap-2"
              >
                <div className="min-w-0 flex-1">
                  <PrimitiveField
                    name={`${name}-${index}`}
                    schema={itemSchema}
                    value={item}
                    required
                    compact
                    suggestions={suggestionsFor(name, catalog)}
                    onChange={(next) => setItem(index, next)}
                  />
                </div>
                <button
                  type="button"
                  onClick={() => remove(id)}
                  disabled={exiting[id] === true}
                  className="content-icon-button h-[38px] w-[38px] shrink-0 text-slate-400 hover:bg-rose-50 hover:text-rose-600"
                  aria-label={t("forms.schema.remove", { label, index: index + 1 })}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            );
          }

          const expanded = open[id] !== false;
          return (
            <div key={id} {...animationProps(id)} className="array-item">
              <div className="accordion-row flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setOpen((previous) => ({ ...previous, [id]: !expanded }))}
                  className="flex min-w-0 flex-1 items-center gap-1.5 text-left"
                  aria-expanded={expanded}
                >
                  <ChevronDown
                    className={cn(
                      "h-4 w-4 shrink-0 text-slate-400 transition-transform duration-200",
                      expanded ? "rotate-0" : "-rotate-90",
                    )}
                  />
                  <span className="truncate text-accordion-title font-medium text-slate-700">
                    {itemTitle(item, index, t)}
                  </span>
                  {isRecord(item) && (
                    <span className="shrink-0 text-3xs text-slate-400">
                      · {t("forms.schema.fields", { count: Object.keys(item).length })}
                    </span>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => remove(id)}
                  disabled={exiting[id] === true}
                  className="content-icon-button text-slate-400 hover:bg-rose-50 hover:text-rose-600"
                  aria-label={t("forms.schema.remove", { label, index: index + 1 })}
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              <div className="accordion-panel" data-open={expanded}>
                <div>
                  <div className="pb-3 pl-5 pt-3">
                    <Fields
                      schema={itemSchema}
                      value={item}
                      catalog={catalog}
                      onChange={(next) => setItem(index, next)}
                    />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
        {!items.length && <p className="py-2 text-2xs text-slate-400">{t("forms.schema.noEntries")}</p>}
      </div>
    </div>
  );
}

function Fields({
  schema,
  value,
  catalog,
  onChange,
}: {
  schema: Schema;
  value: unknown;
  catalog?: Catalog;
  onChange: (value: Record<string, unknown>) => void;
}) {
  const record = isRecord(value) ? value : {};
  return (
    <div className="grid gap-5 sm:grid-cols-2">
      {Object.entries(schema.properties ?? {}).map(([key, child]) => (
        <Field
          key={key}
          name={key}
          schema={child}
          value={record[key]}
          required={(schema.required ?? []).includes(key)}
          catalog={catalog}
          onChange={(next) => onChange({ ...record, [key]: next })}
        />
      ))}
    </div>
  );
}

function Field({
  name,
  schema,
  value,
  required,
  catalog,
  onChange,
}: {
  name: string;
  schema: Schema;
  value: unknown;
  required: boolean;
  catalog?: Catalog;
  onChange: (value: unknown) => void;
}) {
  const { t } = useTranslation();
  const type = schemaType(schema);
  const label = schema.title ?? labelFor(name, t);

  if (type === "object") {
    return (
      <div className="border-l border-slate-200 pl-3 sm:col-span-2">
        <p className="mb-2 text-3xs font-semibold uppercase tracking-wider text-slate-400">
          {label} {required && <span className="text-rose-400">*</span>}
        </p>
        <Fields
          schema={schema}
          value={value}
          catalog={catalog}
          onChange={(next) => onChange(next)}
        />
      </div>
    );
  }

  if (type === "array") {
    return (
      <ArrayField
        name={name}
        schema={schema}
        value={value}
        catalog={catalog}
        onChange={(next) => onChange(next)}
      />
    );
  }

  return (
    <PrimitiveField
      name={name}
      schema={schema}
      value={value}
      required={required}
      suggestions={suggestionsFor(name, catalog)}
      onChange={onChange}
    />
  );
}

export function SchemaForm({
  schema,
  value,
  catalog,
  onChange,
}: {
  schema: Schema;
  value: Record<string, unknown>;
  catalog?: Catalog;
  onChange: (value: Record<string, unknown>) => void;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-card">
      <Fields schema={schema} value={value} catalog={catalog} onChange={(next) => onChange(next)} />
    </div>
  );
}
