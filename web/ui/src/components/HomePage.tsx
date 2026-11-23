import type { LucideIcon } from "lucide-react";
import {
  ArrowRight,
  ArrowUpRight,
  CircleCheck,
  FileDiff,
  GitBranch,
  LockKeyhole,
  Radar,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import { toolIcon } from "../lib/toolIcons";
import type { ToolInfo } from "../lib/types";
import { accentFor, cn, displayToolName } from "../lib/utils";

type ToolStory = {
  questionKey: string;
  detailKey: string;
  evidenceKey: string;
};

const TOOL_STORIES: Record<string, ToolStory> = {
  atlas: {
    questionKey: "home.tool.atlas.question",
    detailKey: "home.tool.atlas.detail",
    evidenceKey: "home.tool.atlas.evidence",
  },
  failover: {
    questionKey: "home.tool.failover.question",
    detailKey: "home.tool.failover.detail",
    evidenceKey: "home.tool.failover.evidence",
  },
  ark: {
    questionKey: "home.tool.ark.question",
    detailKey: "home.tool.ark.detail",
    evidenceKey: "home.tool.ark.evidence",
  },
  ballast: {
    questionKey: "home.tool.ballast.question",
    detailKey: "home.tool.ballast.detail",
    evidenceKey: "home.tool.ballast.evidence",
  },
  vitals: {
    questionKey: "home.tool.vitals.question",
    detailKey: "home.tool.vitals.detail",
    evidenceKey: "home.tool.vitals.evidence",
  },
  custodian: {
    questionKey: "home.tool.custodian.question",
    detailKey: "home.tool.custodian.detail",
    evidenceKey: "home.tool.custodian.evidence",
  },
  crucible: {
    questionKey: "home.tool.crucible.question",
    detailKey: "home.tool.crucible.detail",
    evidenceKey: "home.tool.crucible.evidence",
  },
};

const FALLBACK_STORY: ToolStory = {
  questionKey: "home.tool.fallback.question",
  detailKey: "home.tool.fallback.detail",
  evidenceKey: "home.tool.fallback.evidence",
};

const PRINCIPLES: {
  index: string;
  titleKey: string;
  bodyKey: string;
  icon: LucideIcon;
  tone: string;
}[] = [
  {
    index: "01",
    titleKey: "home.principle.1.title",
    bodyKey: "home.principle.1.body",
    icon: FileDiff,
    tone: "bg-sky-50 text-sky-700",
  },
  {
    index: "02",
    titleKey: "home.principle.2.title",
    bodyKey: "home.principle.2.body",
    icon: GitBranch,
    tone: "bg-violet-50 text-violet-700",
  },
  {
    index: "03",
    titleKey: "home.principle.3.title",
    bodyKey: "home.principle.3.body",
    icon: ShieldCheck,
    tone: "bg-emerald-50 text-emerald-700",
  },
];

const AUDIENCES: { titleKey: string; bodyKey: string; icon: LucideIcon }[] = [
  {
    titleKey: "home.audience.1.title",
    bodyKey: "home.audience.1.body",
    icon: Radar,
  },
  {
    titleKey: "home.audience.2.title",
    bodyKey: "home.audience.2.body",
    icon: CircleCheck,
  },
  {
    titleKey: "home.audience.3.title",
    bodyKey: "home.audience.3.body",
    icon: LockKeyhole,
  },
  {
    titleKey: "home.audience.4.title",
    bodyKey: "home.audience.4.body",
    icon: Sparkles,
  },
];

const RHYTHM: { titleKey: string; bodyKey: string }[] = [
  {
    titleKey: "home.rhythm.step.1.title",
    bodyKey: "home.rhythm.step.1.body",
  },
  {
    titleKey: "home.rhythm.step.2.title",
    bodyKey: "home.rhythm.step.2.body",
  },
  {
    titleKey: "home.rhythm.step.3.title",
    bodyKey: "home.rhythm.step.3.body",
  },
  {
    titleKey: "home.rhythm.step.4.title",
    bodyKey: "home.rhythm.step.4.body",
  },
];

const LOOP_STEPS = [
  "home.loop.step.1",
  "home.loop.step.2",
  "home.loop.step.3",
  "home.loop.step.4",
];

function scrollToSection(id: string) {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.getElementById(id)?.scrollIntoView({
    behavior: reduced ? "auto" : "smooth",
    block: "start",
  });
}

export function HomePage({
  tools,
  version,
  onOpenTool,
}: {
  tools: ToolInfo[];
  version?: string;
  onOpenTool: (toolId: string) => void;
}) {
  const { t } = useTranslation();

  return (
    <div className="mx-auto w-full max-w-[1320px] space-y-16 px-7 py-10 xl:px-10 xl:py-12">
      <section className="home-hero relative overflow-hidden rounded-[28px] border border-slate-800 bg-slate-950 px-8 py-12 text-white shadow-[0_28px_80px_-36px_rgba(15,23,42,.72)] xl:px-12 xl:py-14">
        <div className="home-hero-glow" aria-hidden="true" />
        <div className="relative grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <div>
            <p className="text-3xs font-semibold uppercase tracking-[0.24em] text-sky-300">
              {t("home.hero.eyebrow")}
            </p>
            <h1 className="mt-5 max-w-3xl text-5xl font-semibold leading-[1.06] tracking-[-0.045em] xl:text-[3.7rem]">
              {t("home.hero.headline.start")}{" "}
              <span className="text-sky-300">{t("home.hero.headline.accent")}</span>
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-slate-300">
              {t("home.hero.paragraph")}
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => scrollToSection("home-tools")}
                className="content-button border-slate-700 bg-white text-slate-900 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-300/60"
              >
                {t("home.hero.cta.explore")}
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
              <button
                type="button"
                onClick={() => scrollToSection("home-method")}
                className="content-button border-white/15 bg-white/5 text-slate-200 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-sky-300/40"
              >
                {t("home.hero.cta.method")}
              </button>
            </div>
            <div className="mt-9 flex flex-wrap gap-x-6 gap-y-2 text-2xs text-slate-400">
              <span>{t("home.hero.trust.local")}</span>
              <span aria-hidden="true">·</span>
              <span>{t("home.hero.trust.noCredentials")}</span>
              <span aria-hidden="true">·</span>
              <span>{t("home.hero.trust.seven")}</span>
            </div>
          </div>

          <div className="relative">
            <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-slate-400">
                  {t("home.loop.title")}
                </p>
                <Sparkles className="h-4 w-4 text-sky-300" />
              </div>
              <div className="home-hero-logo mx-auto my-6" aria-hidden="true" />
              <ol className="space-y-3">
                {LOOP_STEPS.map((stepKey, index) => (
                  <li
                    key={stepKey}
                    className="flex items-center gap-3 rounded-xl border border-white/10 bg-slate-900/60 px-4 py-3 text-sm text-slate-200"
                  >
                    <span className="font-mono text-3xs text-sky-300">
                      0{index + 1}
                    </span>
                    <span className="font-medium">{t(stepKey)}</span>
                    <span className="ml-auto h-1.5 w-1.5 rounded-full bg-sky-400/80" />
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </div>
      </section>

      <section id="home-why" className="scroll-mt-8">
        <div className="max-w-4xl">
          <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-slate-500">
            {t("home.why.eyebrow")}
          </p>
          <h2 className="mt-3 text-4xl font-semibold leading-[1.14] tracking-[-0.035em] text-slate-900">
            {t("home.why.headline.first")}
            <br />
            {t("home.why.headline.second")}
          </h2>
          <p className="mt-5 max-w-3xl text-lg leading-relaxed text-slate-600">
            {t("home.why.paragraph")}
          </p>
        </div>

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {PRINCIPLES.map(({ index, titleKey, bodyKey, icon: Icon, tone }) => (
            <article
              key={titleKey}
              className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-card"
            >
              <div className="flex items-start justify-between">
                <span className={cn("grid h-11 w-11 place-items-center rounded-xl", tone)}>
                  <Icon className="h-5 w-5" />
                </span>
                <span className="font-mono text-3xs text-slate-400">{index}</span>
              </div>
              <h3 className="mt-5 text-lg font-semibold tracking-tight text-slate-900">{t(titleKey)}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{t(bodyKey)}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-card xl:p-10">
        <div className="grid gap-10 lg:grid-cols-[0.85fr_1.15fr] lg:items-start">
          <div>
            <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-slate-500">
              {t("home.who.eyebrow")}
            </p>
            <h2 className="mt-3 text-4xl font-semibold leading-[1.14] tracking-[-0.035em] text-slate-900">
              {t("home.who.headline.start")}{" "}
              <em className="font-medium text-sky-700">{t("home.who.headline.emphasis")}</em>
            </h2>
            <p className="mt-5 max-w-xl text-base leading-relaxed text-slate-600">
              {t("home.who.paragraph")}
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {AUDIENCES.map(({ titleKey, bodyKey, icon: Icon }) => (
              <div
                key={titleKey}
                className="rounded-2xl border border-slate-200 bg-slate-50/70 p-5 transition hover:border-slate-300 hover:bg-white"
              >
                <Icon className="h-5 w-5 text-slate-500" />
                <h3 className="mt-4 text-sm font-semibold text-slate-900">{t(titleKey)}</h3>
                <p className="mt-2 text-xs leading-relaxed text-slate-600">{t(bodyKey)}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="home-tools" className="scroll-mt-8">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <div className="max-w-3xl">
            <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-slate-500">
              {t("home.tools.eyebrow")}
            </p>
            <h2 className="mt-3 text-4xl font-semibold leading-[1.14] tracking-[-0.035em] text-slate-900">
              {t("home.tools.headline")}
            </h2>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-600">
              {t("home.tools.paragraph")}
            </p>
          </div>
          <span className="rounded-full border border-slate-200 bg-white px-3 py-1 font-mono text-3xs text-slate-500">
            {t("home.tools.count", {
              total: tools.length || 7,
              version: version ?? "0.1.0",
            })}
          </span>
        </div>

        <div className="mt-9 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {tools.map((tool, index) => {
            const Icon = toolIcon(tool.icon);
            const accent = accentFor(tool.accent);
            const story = TOOL_STORIES[tool.id] ?? FALLBACK_STORY;
            return (
              <button
                key={tool.id}
                type="button"
                onClick={() => onOpenTool(tool.id)}
                className={cn(
                  "group flex h-full flex-col rounded-2xl border border-white/20 p-6 text-left shadow-card transition duration-200 hover:-translate-y-0.5 hover:brightness-105 hover:shadow-[0_18px_40px_-24px_rgba(15,23,42,.45)] focus:outline-none focus:ring-2 focus:ring-white/70 focus:ring-offset-2",
                  accent.solid,
                )}
              >
                <div className="flex items-start justify-between">
                  <span className="grid h-12 w-12 place-items-center rounded-xl bg-white/15 text-white ring-1 ring-white/25">
                    <Icon className="h-5 w-5" />
                  </span>
                  <span className="font-mono text-3xs text-white/60">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>
                <h3 className="mt-6 text-xl font-semibold tracking-tight text-white">
                  {displayToolName(tool.name)}
                </h3>
                <p className="mt-1 text-xs font-semibold text-white/80">{tool.tagline}</p>
                <p className="mt-5 text-sm font-medium leading-relaxed text-white">
                  {t(story.questionKey)}
                </p>
                <p className="mt-2 text-xs leading-relaxed text-white/75">{t(story.detailKey)}</p>
                <div className="mt-auto flex items-center justify-between gap-3 border-t border-white/20 pt-5">
                  <span className="text-3xs leading-snug text-white/70">{t(story.evidenceKey)}</span>
                  <span className="content-button border border-white/30 bg-white/10 text-white transition group-hover:border-white group-hover:bg-white group-hover:text-slate-900">
                    {t("home.tools.open")}
                    <ArrowUpRight className="h-3.5 w-3.5" />
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      <section id="home-method" className="scroll-mt-8 overflow-hidden rounded-[28px] bg-slate-900 px-8 py-12 text-white xl:px-12">
        <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
          <div>
            <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-sky-300">
              {t("home.rhythm.eyebrow")}
            </p>
            <h2 className="mt-3 text-4xl font-semibold leading-[1.14] tracking-[-0.035em]">
              {t("home.rhythm.headline")}
            </h2>
            <p className="mt-5 max-w-lg text-base leading-relaxed text-slate-300">
              {t("home.rhythm.paragraph")}
            </p>
          </div>
          <ol className="grid gap-3 sm:grid-cols-2">
            {RHYTHM.map((step, index) => (
              <li
                key={step.titleKey}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 transition hover:bg-white/[0.07]"
              >
                <span className="font-mono text-3xs text-sky-300">0{index + 1}</span>
                <h3 className="mt-3 text-sm font-semibold text-white">{t(step.titleKey)}</h3>
                <p className="mt-2 text-xs leading-relaxed text-slate-400">{t(step.bodyKey)}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="flex flex-col gap-6 rounded-3xl border border-sky-200 bg-sky-50 p-8 md:flex-row md:items-center md:justify-between xl:p-10">
        <div className="max-w-2xl">
          <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-sky-700">
            {t("home.final.eyebrow")}
          </p>
          <h2 className="mt-3 text-3xl font-semibold leading-tight tracking-tight text-slate-900">
            {t("home.final.headline")}
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">
            {t("home.final.paragraph")}
          </p>
        </div>
        <button
          type="button"
          onClick={() => onOpenTool("atlas")}
          className="content-button shrink-0 bg-slate-900 px-5 py-2.5 text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-400/60"
        >
          {t("home.final.cta", { tool: "Atlas" })}
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </section>

      <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-6 text-2xs text-slate-500">
        <span>{t("home.footer.suite", { version: version ?? "0.1.0" })}</span>
        <span>{t("home.footer.local")}</span>
      </footer>
    </div>
  );
}
