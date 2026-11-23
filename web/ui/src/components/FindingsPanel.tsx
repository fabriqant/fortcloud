import { CircleCheck, CircleX, TriangleAlert } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { RunResult } from "../lib/types";
import { Badge, Card, CardTitle } from "./ui";

export function FindingsPanel({ result }: { result: RunResult | null }) {
  const { t } = useTranslation();
  const errors = result?.errors ?? [];
  const warnings = result?.warnings ?? [];
  const passed = result?.ok && errors.length === 0 && warnings.length === 0;

  return (
    <Card className="h-full">
      <CardTitle title={t("feedback.findings.title")} subtitle={t("feedback.findings.subtitle")} />
      <p className="mb-5 mt-7 text-2xs leading-relaxed text-slate-500">
        {t("feedback.findings.guidance")}
      </p>
      <div className="mb-4 flex flex-wrap gap-2">
        <Badge tone={errors.length ? "rose" : "green"}>
          {t("feedback.findings.errorsCount", { count: errors.length })}
        </Badge>
        <Badge tone={warnings.length ? "amber" : "slate"}>
          {t("feedback.findings.warningsCount", { count: warnings.length })}
        </Badge>
        {result?.strict && <Badge tone="blue">{t("feedback.findings.strict")}</Badge>}
      </div>

      {!result && (
        <p className="rounded-lg bg-slate-50 p-4 text-xs leading-relaxed text-slate-500">
          {t("feedback.findings.emptyPrefix")}{" "}
          <span className="font-semibold text-slate-700">{t("feedback.findings.validate")}</span>{" "}
          {t("feedback.findings.emptyOr")}{" "}
          <span className="font-semibold text-slate-700">{t("feedback.findings.check")}</span>{" "}
          {t("feedback.findings.emptySuffix")}
        </p>
      )}

      {result && passed && (
        <div className="flex items-start gap-2 rounded-lg bg-emerald-50 p-3 text-xs text-emerald-800">
          <CircleCheck className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{t("feedback.findings.noFindings")}</span>
        </div>
      )}

      {errors.length > 0 && (
        <div className="space-y-2">
          <p className="text-3xs font-semibold uppercase tracking-wider text-rose-600">{t("feedback.findings.errors")}</p>
          {errors.map((message, index) => (
            <div key={`e-${index}`} className="flex gap-2 rounded-lg bg-rose-50 p-2.5 text-2xs leading-relaxed text-rose-900">
              <CircleX className="mt-0.5 h-3.5 w-3.5 shrink-0 text-rose-500" />
              <span className="break-words">{message}</span>
            </div>
          ))}
        </div>
      )}

      {warnings.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-3xs font-semibold uppercase tracking-wider text-amber-600">{t("feedback.findings.warnings")}</p>
          {warnings.map((message, index) => (
            <div key={`w-${index}`} className="flex gap-2 rounded-lg bg-amber-50 p-2.5 text-2xs leading-relaxed text-amber-900">
              <TriangleAlert className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
              <span className="break-words">{message}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
