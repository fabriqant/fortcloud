import { BookOpen, ExternalLink, Github, Mail } from "lucide-react";
import type { ToolInfo } from "../lib/types";
import { toolIcon } from "../lib/toolIcons";
import { accentFor, cn, displayToolName } from "../lib/utils";

export function ToolSidebar({
  tools,
  activeId,
  version,
  onSelect,
}: {
  tools: ToolInfo[];
  activeId: string;
  version?: string;
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
    <aside className="app-sidebar sticky top-0 flex w-[268px] shrink-0 flex-col border-r border-slate-200 bg-slate-950 text-slate-300">
      <div className="flex shrink-0 items-center justify-center border-b border-slate-800 px-5 py-5">
        <div className="sidebar-logo" role="img" aria-label="Fortcloud" />
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        {tools.map((tool) => {
          const Icon = toolIcon(tool.icon);
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
              <Icon
                className={cn(
                  "mt-0.5 h-6 w-6 shrink-0",
                  active ? accent.text : "text-slate-400",
                )}
              />
              <span className="min-w-0">
                <span className={cn("block truncate text-sm font-semibold", active ? "text-white" : "text-slate-300")}>
                  {displayToolName(tool.name)}
                </span>
                <span className="mt-0.5 block truncate text-sidebar-desc font-medium text-slate-500">
                  {tool.tagline}
                </span>
              </span>
            </button>
          );
        })}
      </nav>

      <div className="shrink-0 border-t border-slate-800 px-5 py-4">
        <div className="space-y-0.5">
          {links.map(({ label, href, icon: Icon, external }) => (
            <a
              key={label}
              href={href}
              target={external ? "_blank" : undefined}
              rel={external ? "noreferrer" : undefined}
              className="group flex items-center gap-2 rounded-md px-2 py-1.5 text-footer text-slate-400 transition hover:bg-slate-900 hover:text-white"
            >
              <Icon className="h-3.5 w-3.5 shrink-0 text-slate-500 group-hover:text-sky-400" />
              <span className="min-w-0 flex-1 truncate">{label}</span>
              {external && <ExternalLink className="h-3 w-3 shrink-0 text-slate-600 group-hover:text-slate-400" />}
            </a>
          ))}
        </div>

        <div className="mt-3 border-t border-slate-800 pt-3">
          <div className="flex items-center gap-2 text-footer text-slate-400">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_0_3px_rgba(52,211,153,.15)]" />
            Local mode · no cloud access
          </div>
          <p className="mt-1.5 text-footer text-slate-600">
            Models stay in <span className="font-mono text-slate-500">web/workspaces/</span>
          </p>
          {version && (
            <div className="mt-2 flex items-center justify-between gap-2 text-footer text-slate-600">
              <span>Fortcloud suite</span>
              <span className="font-mono text-slate-500">v{version}</span>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
