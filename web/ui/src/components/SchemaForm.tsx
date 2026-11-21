import { Plus, Trash2 } from "lucide-react";
import { cn } from "../lib/utils";

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

function labelFor(name: string): string {
  return name.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
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
  onChange,
}: {
  name: string;
  schema: Schema;
  value: unknown;
  required: boolean;
  onChange: (value: unknown) => void;
}) {
  const type = schemaType(schema);
  const label = schema.title ?? labelFor(name);
  const inputClass =
    "w-full rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-[11px] text-slate-800 outline-none focus:border-slate-400";

  if (allowsNull(schema) && value === null) {
    return (
      <label className="block">
        <span className="mb-1 block text-[10px] font-semibold text-slate-500">
          {label} <span className="font-normal text-slate-400">· null</span>
        </span>
        <button
          type="button"
          onClick={() => onChange(blankFor(schema))}
          className={cn(inputClass, "text-left text-slate-400 hover:border-slate-400")}
        >
          Set a value
        </button>
      </label>
    );
  }

  let control;
  if (schema.enum) {
    control = (
      <select className={inputClass} value={String(value ?? "")} onChange={(event) => onChange(event.target.value)}>
        {!required && <option value="">—</option>}
        {schema.enum.map((option) => (
          <option key={String(option)} value={String(option)}>
            {String(option)}
          </option>
        ))}
      </select>
    );
  } else if (schema.const !== undefined) {
    control = <input className={cn(inputClass, "bg-slate-50 text-slate-500")} value={String(schema.const)} disabled />;
  } else if (type === "boolean") {
    control = (
      <label className="flex items-center gap-2 pt-1 text-[11px] text-slate-600">
        <input
          type="checkbox"
          checked={Boolean(value)}
          onChange={(event) => onChange(event.target.checked)}
          className="h-3.5 w-3.5 rounded border-slate-300"
        />
        Enabled
      </label>
    );
  } else if (type === "integer" || type === "number") {
    control = (
      <input
        type="number"
        className={inputClass}
        value={value === undefined || value === null ? "" : String(value)}
        min={schema.minimum}
        max={schema.maximum}
        onChange={(event) =>
          onChange(event.target.value === "" ? "" : Number(event.target.value))
        }
      />
    );
  } else {
    control = (
      <input
        type="text"
        className={cn(inputClass, "font-mono")}
        value={value === undefined || value === null ? "" : String(value)}
        placeholder={schema.pattern ? "Must match the schema pattern" : undefined}
        onChange={(event) => onChange(event.target.value)}
      />
    );
  }

  return (
    <label className="block">
      <span className="mb-1 block text-[10px] font-semibold text-slate-500">
        {label} {required && <span className="text-rose-400">*</span>}
      </span>
      {control}
    </label>
  );
}

function Fields({
  schema,
  value,
  onChange,
}: {
  schema: Schema;
  value: unknown;
  onChange: (value: Record<string, unknown>) => void;
}) {
  const record = isRecord(value) ? value : {};
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {Object.entries(schema.properties ?? {}).map(([key, child]) => (
        <Field
          key={key}
          name={key}
          schema={child}
          value={record[key]}
          required={(schema.required ?? []).includes(key)}
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
  onChange,
}: {
  name: string;
  schema: Schema;
  value: unknown;
  required: boolean;
  onChange: (value: unknown) => void;
}) {
  const type = schemaType(schema);
  const label = schema.title ?? labelFor(name);

  if (type === "object") {
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-3 sm:col-span-2">
        <p className="mb-2.5 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          {label} {required && <span className="text-rose-400">*</span>}
        </p>
        <Fields
          schema={schema}
          value={value}
          onChange={(next) => onChange(next)}
        />
      </div>
    );
  }

  if (type === "array") {
    const items = Array.isArray(value) ? value : [];
    const itemSchema = schema.items ?? {};
    return (
      <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-3 sm:col-span-2">
        <div className="mb-2.5 flex items-center justify-between gap-2">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            {label} <span className="text-slate-300">· {items.length}</span>
          </p>
          <button
            type="button"
            onClick={() => onChange([...items, blankFor(itemSchema)])}
            className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2 py-1 text-[10px] font-semibold text-slate-600 hover:border-slate-400"
          >
            <Plus className="h-3 w-3" /> Add
          </button>
        </div>
        <div className="space-y-2">
          {items.map((item, index) => (
            <div key={index} className="rounded-md border border-slate-200 bg-white p-3">
              <div className="mb-2 flex items-center justify-between">
                <span className="font-mono text-[10px] text-slate-400">#{index + 1}</span>
                <button
                  type="button"
                  onClick={() => onChange(items.filter((_, position) => position !== index))}
                  className="text-slate-400 hover:text-rose-600"
                  aria-label={`Remove ${name} ${index + 1}`}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
              {schemaType(itemSchema) === "object" ? (
                <Fields schema={itemSchema} value={item} onChange={(next) => {
                  const copy = [...items];
                  copy[index] = next;
                  onChange(copy);
                }} />
              ) : (
                <PrimitiveField
                  name={`${name}-${index}`}
                  schema={itemSchema}
                  value={item}
                  required
                  onChange={(next) => {
                    const copy = [...items];
                    copy[index] = next;
                    onChange(copy);
                  }}
                />
              )}
            </div>
          ))}
          {!items.length && <p className="py-2 text-center text-[11px] text-slate-400">No entry yet.</p>}
        </div>
      </div>
    );
  }

  return (
    <PrimitiveField name={name} schema={schema} value={value} required={required} onChange={onChange} />
  );
}

export function SchemaForm({
  schema,
  value,
  onChange,
}: {
  schema: Schema;
  value: Record<string, unknown>;
  onChange: (value: Record<string, unknown>) => void;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-card">
      <Fields schema={schema} value={value} onChange={(next) => onChange(next)} />
    </div>
  );
}
