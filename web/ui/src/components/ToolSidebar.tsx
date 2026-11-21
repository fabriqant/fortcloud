import {
  Activity,
  Archive,
  BookOpen,
  Boxes,
  ExternalLink,
  FlaskConical,
  Gauge,
  Github,
  Mail,
  Network,
  ShieldCheck,
  Shuffle,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { ToolInfo } from "../lib/types";
import { accentFor, cn } from "../lib/utils";

const ICONS: Record<string, LucideIcon> = {
  network: Network,
  shuffle: Shuffle,
  archive: Archive,
  gauge: Gauge,
  activity: Activity,
  shield: ShieldCheck,
  flask: FlaskConical,
};

export function ToolSidebar({
  tools,
  activeId,
  onSelect,
}: {
  tools: ToolInfo[];
  activeId: string;
  onSelect: (id: string) => void;
}) {
  const docsUrl = activeId
    ? `https://github.com/fabriqant/fortcloud-io/blob/main/${activeId}/README.md`
    : "https://github.com/fabriqant/fortcloud-io#readme";

  const links = [
    { label: "Documentation", href: docsUrl, icon: BookOpen, external: true },
    {
      label: "GitHub repository",
      href: "https://github.com/fabriqant/fortcloud-io",
      icon: Github,
      external: true,
    },
    {
      label: "fabriqant@gmail.com",
      href: "mailto:fabriqant@gmail.com",
      icon: Mail,
      external: false,
    },
  ];

  return (
    <aside className="flex w-[268px] shrink-0 flex-col border-r border-slate-200 bg-slate-950 text-slate-300">
      <div className="border-b border-slate-800 px-5 py-5">
        <div className="flex items-center gap-2.5">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-sky-400 to-indigo-600 text-sm font-black text-white">
            F
          </div>
          <div>
            <p className="text-sm font-bold tracking-[0.18em] text-white">FORTCLOUD</p>
            <p className="text-[10px] tracking-[0.18em] text-slate-500">by fabriqant</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        <p className="px-2 pb-2 text-[10px] font-semibold uppercase tracking-widest text-slate-500">
          Tools · {tools.length}
        </p>
        {tools.map((tool) => {
          const Icon = ICONS[tool.icon] ?? Boxes;
          const accent = accentFor(tool.accent);
          const active = tool.id === activeId;
          return (
            <button
              key={tool.id}
              onClick={() => onSelect(tool.id)}
              className={cn(
                "group flex w-full items-start gap-3 rounded-lg px-3 py-2.5 text-left transition",
                active ? "bg-slate-800 ring-1 ring-slate-700" : "hover:bg-slate-900",
              )}
            >
              <span
                className={cn(
                  "mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-md",
                  active ? accent.soft : "bg-slate-800/70",
                )}
              >
                <Icon className={cn("h-3.5 w-3.5", active ? accent.text : "text-slate-400")} />
              </span>
              <span className="min-w-0">
                <span className={cn("block truncate text-xs font-semibold", active ? "text-white" : "text-slate-300")}>
                  {tool.name}
                </span>
                <span className="mt-0.5 block truncate text-[10px] leading-snug text-slate-500">
                  {tool.tagline}
                </span>
              </span>
            </button>
          );
        })}
      </nav>

      <div className="border-t border-slate-800 px-5 py-4">
        <div className="space-y-0.5">
          {links.map(({ label, href, icon: Icon, external }) => (
            <a
              key={label}
              href={href}
              target={external ? "_blank" : undefined}
              rel={external ? "noreferrer" : undefined}
              className="group flex items-center gap-2 rounded-md px-2 py-1.5 text-[11px] text-slate-400 transition hover:bg-slate-900 hover:text-white"
            >
              <Icon className="h-3.5 w-3.5 shrink-0 text-slate-500 group-hover:text-sky-400" />
              <span className="min-w-0 flex-1 truncate">{label}</span>
              {external && <ExternalLink className="h-3 w-3 shrink-0 text-slate-600 group-hover:text-slate-400" />}
            </a>
          ))}
        </div>

        <div className="mt-3 border-t border-slate-800 pt-3">
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_0_3px_rgba(52,211,153,.15)]" />
            Local mode · no cloud access
          </div>
          <p className="mt-1.5 text-[10px] leading-relaxed text-slate-600">
            Models stay in <span className="font-mono text-slate-500">web/workspaces/</span>
          </p>
        </div>
      </div>
    </aside>
  );
}
