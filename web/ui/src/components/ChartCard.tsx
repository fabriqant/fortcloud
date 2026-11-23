import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useTranslation } from "react-i18next";
import type { ChartSeries } from "../lib/types";
import { Card, CardTitle } from "./ui";

const COLORS = ["#e11d48", "#f59e0b", "#0ea5e9", "#10b981", "#8b5cf6", "#ec4899", "#64748b"];

export function ChartCard({ chart }: { chart: ChartSeries }) {
  const { t } = useTranslation();
  const data = chart.data.filter((entry) => entry.value > 0);
  const display = data.length ? data : [{ name: t("feedback.chart.none"), value: 0 }];

  return (
    <Card>
      <CardTitle title={chart.label} subtitle={t("feedback.chart.subtitle")} />
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          {chart.type === "donut" ? (
            <PieChart>
              <Pie
                data={display}
                dataKey="value"
                nameKey="name"
                innerRadius={58}
                outerRadius={88}
                paddingAngle={3}
                stroke="none"
              >
                {display.map((entry, index) => (
                  <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ borderRadius: 10, border: "1px solid #e2e8f0", fontSize: 12 }}
              />
            </PieChart>
          ) : (
            <BarChart data={display} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip
                cursor={{ fill: "#f1f5f9" }}
                contentStyle={{ borderRadius: 10, border: "1px solid #e2e8f0", fontSize: 12 }}
              />
              <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={52}>
                {display.map((entry, index) => (
                  <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
      {chart.type === "donut" && (
        <div className="mt-3 flex flex-wrap justify-center gap-x-4 gap-y-1.5">
          {display.map((entry, index) => (
            <span key={entry.name} className="flex items-center gap-1.5 text-2xs text-slate-600">
              <span className="h-2 w-2 rounded-full" style={{ background: COLORS[index % COLORS.length] }} />
              {entry.name} · {entry.value}
            </span>
          ))}
        </div>
      )}
    </Card>
  );
}
