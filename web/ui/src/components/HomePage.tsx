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
import { toolIcon } from "../lib/toolIcons";
import type { ToolInfo } from "../lib/types";
import { accentFor, cn, displayToolName } from "../lib/utils";

type ToolStory = {
  question: string;
  detail: string;
  evidence: string;
};

const TOOL_STORIES: Record<string, ToolStory> = {
  atlas: {
    question: "Where is the risk, and what is the blast radius?",
    detail:
      "Atlas draws the system as a graph, then names the single points of failure, single-region P0s and uncovered resilience promises hiding inside it.",
    evidence: "Dependency graph · resilience report",
  },
  failover: {
    question: "Could we really switch over in time?",
    detail:
      "Failover checks that every critical service has a real standby, a detection path, a promotion plan, enough capacity and a drill recent enough to trust.",
    evidence: "Failover matrix · drill scenarios",
  },
  ark: {
    question: "Do our restores actually work?",
    detail:
      "Ark treats backup as a claim that needs evidence. It checks coverage, immutability, retention and dated restore tests instead of accepting a green checkbox.",
    evidence: "Backup coverage · restore evidence",
  },
  ballast: {
    question: "What happens to latency when a dependency fails?",
    detail:
      "Ballast adds up the worst-case timeout budget, then checks retries, breakers, bulkheads and fallbacks so a slow call cannot quietly take down the chain.",
    evidence: "Timeout budget · policy matrix",
  },
  vitals: {
    question: "Would we see a breach early enough?",
    detail:
      "Vitals connects signals, SLOs and verification checks. It keeps objectives honest, alert thresholds meaningful and data quality visible beside uptime.",
    evidence: "SLO dashboard · signal catalog",
  },
  custodian: {
    question: "Can we prove who changed what, and why?",
    detail:
      "Custodian keeps access least-privileged, secrets referenced rather than copied, audit sinks immutable and every production change reviewable and reversible.",
    evidence: "Access matrix · change control",
  },
  crucible: {
    question: "Have we rehearsed the outage?",
    detail:
      "Crucible plans controlled failure drills with four clear roles, communication cadence and verified outcomes — before the real incident writes the script.",
    evidence: "Scenario plan · verification report",
  },
};

const FALLBACK_STORY: ToolStory = {
  question: "What does this tool help us prove?",
  detail: "A focused model, a readable check and evidence your team can review together.",
  evidence: "Generated reports",
};

const PRINCIPLES: { index: string; title: string; body: string; icon: LucideIcon; tone: string }[] = [
  {
    index: "01",
    title: "Make the story explicit",
    body: "Resilience usually lives in slides and headings. FortCloud moves it into small, versioned files where intent, ownership and trade-offs can be read by a human.",
    icon: FileDiff,
    tone: "bg-sky-50 text-sky-700",
  },
  {
    index: "02",
    title: "Review the decision, not the syntax",
    body: "Scenarios and staged imports show exactly what changed. A reviewer can discuss the risk itself — not guess what a dashboard snapshot was supposed to mean.",
    icon: GitBranch,
    tone: "bg-violet-50 text-violet-700",
  },
  {
    index: "03",
    title: "Regenerate evidence on demand",
    body: "Graphs, matrices and status files are rebuilt from the model by check. No hand-maintained report can drift away from the thing it claims to describe.",
    icon: ShieldCheck,
    tone: "bg-emerald-50 text-emerald-700",
  },
];

const AUDIENCES: { title: string; body: string; icon: LucideIcon }[] = [
  {
    title: "Platform & architecture teams",
    body: "See the shape of a system before a redesign, and keep the reasoning next to the diagrams.",
    icon: Radar,
  },
  {
    title: "SRE & reliability engineers",
    body: "Turn failover, restore and latency promises into checks that fail loudly in CI.",
    icon: CircleCheck,
  },
  {
    title: "Security & compliance leads",
    body: "Show least privilege, auditable changes and dated evidence without another spreadsheet.",
    icon: LockKeyhole,
  },
  {
    title: "Teams without a platform budget",
    body: "Start with one tool and one service. No backend, no agent, no new platform to adopt.",
    icon: Sparkles,
  },
];

const RHYTHM: { title: string; body: string }[] = [
  {
    title: "Describe",
    body: "Use the guided form or edit YAML directly. The model stays local and readable.",
  },
  {
    title: "Propose",
    body: "Optional AWS, Azure and GCP connectors suggest an inventory from non-secret identifiers only.",
  },
  {
    title: "Review",
    body: "Read the diff, create a scenario, accept or discard. Nothing is applied silently.",
  },
  {
    title: "Prove",
    body: "Run check locally or in CI. Reports and status files are rebuilt from the model.",
  },
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
  return (
    <div className="mx-auto w-full max-w-[1320px] space-y-16 px-7 py-10 xl:px-10 xl:py-12">
      <section className="home-hero relative overflow-hidden rounded-[28px] border border-slate-800 bg-slate-950 px-8 py-12 text-white shadow-[0_28px_80px_-36px_rgba(15,23,42,.72)] xl:px-12 xl:py-14">
        <div className="home-hero-glow" aria-hidden="true" />
        <div className="relative grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <div>
            <p className="text-3xs font-semibold uppercase tracking-[0.24em] text-sky-300">
              Open-source resilience toolkit
            </p>
            <h1 className="mt-5 max-w-3xl text-5xl font-semibold leading-[1.06] tracking-[-0.045em] xl:text-[3.7rem]">
              Confidence should be <span className="text-sky-300">reviewable.</span>
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-slate-300">
              FortCloud turns the story you tell about your infrastructure into versioned models,
              readable checks and evidence your team can actually discuss — without sending your
              diagrams or credentials anywhere.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => scrollToSection("home-tools")}
                className="content-button border-slate-700 bg-white text-slate-900 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-300/60"
              >
                Explore the seven tools
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
              <button
                type="button"
                onClick={() => scrollToSection("home-method")}
                className="content-button border-white/15 bg-white/5 text-slate-200 hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-sky-300/40"
              >
                See how it works
              </button>
            </div>
            <div className="mt-9 flex flex-wrap gap-x-6 gap-y-2 text-2xs text-slate-400">
              <span>Local by design</span>
              <span aria-hidden="true">·</span>
              <span>No cloud credentials in the browser</span>
              <span aria-hidden="true">·</span>
              <span>Seven independent tools</span>
            </div>
          </div>

          <div className="relative">
            <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.045] p-6 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-slate-400">
                  The quiet loop
                </p>
                <Sparkles className="h-4 w-4 text-sky-300" />
              </div>
              <div className="home-hero-logo mx-auto my-6" aria-hidden="true" />
              <ol className="space-y-3">
                {["Declare the intent", "Check the story", "Review the diff", "Ship the evidence"].map(
                  (step, index) => (
                    <li
                      key={step}
                      className="flex items-center gap-3 rounded-xl border border-white/10 bg-slate-900/60 px-4 py-3 text-sm text-slate-200"
                    >
                      <span className="font-mono text-3xs text-sky-300">
                        0{index + 1}
                      </span>
                      <span className="font-medium">{step}</span>
                      <span className="ml-auto h-1.5 w-1.5 rounded-full bg-sky-400/80" />
                    </li>
                  ),
                )}
              </ol>
            </div>
          </div>
        </div>
      </section>

      <section id="home-why" className="scroll-mt-8">
        <div className="max-w-4xl">
          <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-slate-500">
            Why it exists
          </p>
          <h2 className="mt-3 text-4xl font-semibold leading-[1.14] tracking-[-0.035em] text-slate-900">
            Resilience claims are easy.<br/>Resilience evidence is not.
          </h2>
          <p className="mt-5 max-w-3xl text-lg leading-relaxed text-slate-600">
            Diagrams age. Runbooks drift. A green dashboard rarely explains what happens when a
            region disappears. FortCloud keeps the decision close to the code: a model you can
            review, a check you can run and a report that can be questioned in a pull request.
          </p>
        </div>

        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {PRINCIPLES.map(({ index, title, body, icon: Icon, tone }) => (
            <article
              key={title}
              className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-card"
            >
              <div className="flex items-start justify-between">
                <span className={cn("grid h-11 w-11 place-items-center rounded-xl", tone)}>
                  <Icon className="h-5 w-5" />
                </span>
                <span className="font-mono text-3xs text-slate-400">{index}</span>
              </div>
              <h3 className="mt-5 text-lg font-semibold tracking-tight text-slate-900">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white p-8 shadow-card xl:p-10">
        <div className="grid gap-10 lg:grid-cols-[0.85fr_1.15fr] lg:items-start">
          <div>
            <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-slate-500">
              Who it is for
            </p>
            <h2 className="mt-3 text-4xl font-semibold leading-[1.14] tracking-[-0.035em] text-slate-900">
              For the people who answer when someone asks: <em className="font-medium text-sky-700">“Can we prove it?”</em>
            </h2>
            <p className="mt-5 max-w-xl text-base leading-relaxed text-slate-600">
              You do not need a resilience platform or a dedicated tooling team. You need a calm
              way to state intent, keep it current and show the work. Each tool can be adopted on
              its own.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {AUDIENCES.map(({ title, body, icon: Icon }) => (
              <div
                key={title}
                className="rounded-2xl border border-slate-200 bg-slate-50/70 p-5 transition hover:border-slate-300 hover:bg-white"
              >
                <Icon className="h-5 w-5 text-slate-500" />
                <h3 className="mt-4 text-sm font-semibold text-slate-900">{title}</h3>
                <p className="mt-2 text-xs leading-relaxed text-slate-600">{body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="home-tools" className="scroll-mt-8">
        <div className="flex flex-wrap items-end justify-between gap-6">
          <div className="max-w-3xl">
            <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-slate-500">
              The toolkit
            </p>
            <h2 className="mt-3 text-4xl font-semibold leading-[1.14] tracking-[-0.035em] text-slate-900">
              Seven focused tools. One quiet discipline.
            </h2>
            <p className="mt-5 max-w-2xl text-base leading-relaxed text-slate-600">
              Each tool answers one uncomfortable question and produces its own evidence. Start
              with the question you cannot currently answer.
            </p>
          </div>
          <span className="rounded-full border border-slate-200 bg-white px-3 py-1 font-mono text-3xs text-slate-500">
            {tools.length || 7} tools · v{version ?? "0.1.0"}
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
                  {story.question}
                </p>
                <p className="mt-2 text-xs leading-relaxed text-white/75">{story.detail}</p>
                <div className="mt-auto flex items-center justify-between gap-3 border-t border-white/20 pt-5">
                  <span className="text-3xs leading-snug text-white/70">{story.evidence}</span>
                  <span className="content-button border border-white/30 bg-white/10 text-white transition group-hover:border-white group-hover:bg-white group-hover:text-slate-900">
                    Open
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
              The rhythm
            </p>
            <h2 className="mt-3 text-4xl font-semibold leading-[1.14] tracking-[-0.035em]">
              Declare. Review. Prove. Repeat.
            </h2>
            <p className="mt-5 max-w-lg text-base leading-relaxed text-slate-300">
              The console is deliberately a consumer of the tools. It makes the model easier to
              write and the evidence easier to read — it never becomes another system of record.
            </p>
          </div>
          <ol className="grid gap-3 sm:grid-cols-2">
            {RHYTHM.map((step, index) => (
              <li
                key={step.title}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 transition hover:bg-white/[0.07]"
              >
                <span className="font-mono text-3xs text-sky-300">0{index + 1}</span>
                <h3 className="mt-3 text-sm font-semibold text-white">{step.title}</h3>
                <p className="mt-2 text-xs leading-relaxed text-slate-400">{step.body}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="flex flex-col gap-6 rounded-3xl border border-sky-200 bg-sky-50 p-8 md:flex-row md:items-center md:justify-between xl:p-10">
        <div className="max-w-2xl">
          <p className="text-3xs font-semibold uppercase tracking-[0.22em] text-sky-700">
            A good first step
          </p>
          <h2 className="mt-3 text-3xl font-semibold leading-tight tracking-tight text-slate-900">
            Start with one uncomfortable question.
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">
            If you do not know where to begin, open Atlas with one production service. It will
            show you the risk before the next incident does.
          </p>
        </div>
        <button
          type="button"
          onClick={() => onOpenTool("atlas")}
          className="content-button shrink-0 bg-slate-900 px-5 py-2.5 text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-sky-400/60"
        >
          Open Atlas
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </section>

      <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 pt-6 text-2xs text-slate-500">
        <span>FortCloud suite · v{version ?? "0.1.0"}</span>
        <span>Local console · models stay in web/workspaces/</span>
      </footer>
    </div>
  );
}
