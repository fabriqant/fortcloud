import { CircleCheck, CircleX, TriangleAlert } from "lucide-react";
import type { RunResult } from "../lib/types";
import { Badge, Card, CardTitle } from "./ui";

export function FindingsPanel({ result }: { result: RunResult | null }) {
  const errors = result?.errors ?? [];
  const warnings = result?.warnings ?? [];
  const passed = result?.ok && errors.length === 0 && warnings.length === 0;

  return (
    <Card className="h-full">
      <CardTitle title="Findings" subtitle="Live diagnostics from the last run" />
      <div className="mb-4 flex flex-wrap gap-2">
        <Badge tone={errors.length ? "rose" : "green"}>{errors.length} errors</Badge>
        <Badge tone={warnings.length ? "amber" : "slate"}>{warnings.length} warnings</Badge>
        {result?.strict && <Badge tone="blue">strict</Badge>}
      </div>

      {!result && (
        <p className="rounded-lg bg-slate-50 p-4 text-xs leading-relaxed text-slate-500">
          Run <span className="font-semibold text-slate-700">Validate</span> or{" "}
          <span className="font-semibold text-slate-700">Check</span> to see errors and warnings here.
        </p>
      )}

      {result && passed && (
        <div className="flex items-start gap-2 rounded-lg bg-emerald-50 p-3 text-xs text-emerald-800">
          <CircleCheck className="mt-0.5 h-4 w-4 shrink-0" />
          <span>No findings. The model passes all checks.</span>
        </div>
      )}

      {errors.length > 0 && (
        <div className="space-y-2">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-rose-600">Errors</p>
          {errors.map((message, index) => (
            <div key={`e-${index}`} className="flex gap-2 rounded-lg bg-rose-50 p-2.5 text-[11px] leading-relaxed text-rose-900">
              <CircleX className="mt-0.5 h-3.5 w-3.5 shrink-0 text-rose-500" />
              <span className="break-words">{message}</span>
            </div>
          ))}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-amber-600">Warnings</p>
          {warnings.map((message, index) => (
            <div key={`w-${index}`} className="flex gap-2 rounded-lg bg-amber-50 p-2.5 text-[11px] leading-relaxed text-amber-900">
              <TriangleAlert className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
              <span className="break-words">{message}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
