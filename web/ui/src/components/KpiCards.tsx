import { AlertTriangle, CircleAlert, Layers } from "lucide-react";
import type { Kpi } from "../lib/types";
import { cn } from "../lib/utils";
import { Card } from "./ui";

const TONES = {
  danger: { icon: CircleAlert, ring: "ring-rose-200", iconColor: "text-rose-600", bg: "bg-rose-50" },
  warning: { icon: AlertTriangle, ring: "ring-amber-200", iconColor: "text-amber-600", bg: "bg-amber-50" },
  neutral: { icon: Layers, ring: "ring-slate-200", iconColor: "text-slate-500", bg: "bg-slate-100" },
};

export function KpiCards({ kpis }: { kpis: Kpi[] }) {
  if (!kpis.length) return null;
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {kpis.map((kpi) => {
        const tone = TONES[kpi.tone] ?? TONES.neutral;
        const Icon = tone.icon;
        return (
          <Card key={kpi.key} className={cn("flex items-center gap-4 ring-1", tone.ring)}>
            <span className={cn("grid h-10 w-10 shrink-0 place-items-center rounded-lg", tone.bg)}>
              <Icon className={cn("h-5 w-5", tone.iconColor)} />
            </span>
            <div className="min-w-0">
              <p className="text-2xl font-bold tabular-nums tracking-tight text-slate-900">{kpi.value}</p>
              <p className="truncate text-[11px] font-medium text-slate-500">{kpi.label}</p>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
