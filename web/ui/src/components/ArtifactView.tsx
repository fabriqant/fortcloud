import { Download, FileJson } from "lucide-react";
import { useTranslation } from "react-i18next";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ArtifactInfo, ArtifactPayload } from "../lib/types";
import { Button, Card, CardTitle } from "./ui";
import { GraphView } from "./GraphView";

const markdownStyles =
  "[&_h1]:mt-1 [&_h1]:text-lg [&_h1]:font-bold [&_h1]:text-slate-900 [&_h2]:mt-6 [&_h2]:border-b [&_h2]:border-slate-100 [&_h2]:pb-1.5 [&_h2]:text-sm [&_h2]:font-bold [&_h2]:text-slate-900 [&_h3]:mt-5 [&_h3]:text-xs [&_h3]:font-bold [&_h3]:uppercase [&_h3]:tracking-wider [&_h3]:text-slate-600 [&_p]:mt-2 [&_p]:text-xs [&_p]:leading-relaxed [&_p]:text-slate-600 [&_li]:mt-1 [&_li]:text-xs [&_li]:leading-relaxed [&_li]:text-slate-600 [&_ul]:mt-2 [&_ul]:list-disc [&_ul]:pl-5 [&_code]:rounded [&_code]:bg-slate-100 [&_code]:px-1 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-2xs [&_code]:text-slate-800 [&_pre]:max-w-full [&_pre]:overflow-auto [&_table]:mt-3 [&_table]:w-full [&_table]:min-w-max [&_table]:border-collapse [&_table]:text-2xs [&_th]:border-b [&_th]:border-slate-200 [&_th]:px-2 [&_th]:py-2 [&_th]:text-left [&_th]:font-semibold [&_th]:text-slate-600 [&_td]:border-b [&_td]:border-slate-100 [&_td]:px-2 [&_td]:py-2 [&_td]:align-top [&_td]:text-slate-700 [&_blockquote]:mt-2 [&_blockquote]:rounded [&_blockquote]:bg-sky-50 [&_blockquote]:px-3 [&_blockquote]:py-2 [&_blockquote]:text-2xs [&_blockquote]:text-sky-800 [&_a]:text-sky-600 [&_a]:underline";

function extractMermaid(content: string): string {
  const fenced = content.match(/```mermaid\s*\r?\n([\s\S]*?)\r?\n?```/i)?.[1];
  if (fenced) return fenced.trim();
  const bare = /^\s*(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|gitGraph)/i;
  return bare.test(content) ? content.trim() : "";
}

export function ArtifactView({
  artifact,
  payload,
}: {
  artifact: ArtifactInfo;
  payload: ArtifactPayload | null;
}) {
  const { t } = useTranslation();

  if (!payload) {
    return (
      <Card>
        <CardTitle title={artifact.label} subtitle={artifact.name} />
        <p className="text-xs text-slate-500">{t("feedback.artifact.generateHint")}</p>
      </Card>
    );
  }

  const download = () => {
    const url = URL.createObjectURL(new Blob([payload.content], { type: "text/plain;charset=utf-8" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = payload.name;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (artifact.kind === "mermaid") {
    const graph = extractMermaid(payload.content);
    if (!graph) {
      return (
        <Card>
          <CardTitle title={artifact.label} subtitle={artifact.name} />
          <p className="text-xs text-slate-500">{t("feedback.artifact.noGraph")}</p>
        </Card>
      );
    }
    return <GraphView graph={graph} title={artifact.label} />;
  }

  let pretty = payload.content;
  if (artifact.kind === "json") {
    try {
      pretty = JSON.stringify(JSON.parse(payload.content), null, 2);
    } catch {
      // display raw content
    }
  }

  return (
    <Card>
      <CardTitle
        title={artifact.label}
        subtitle={`${artifact.name} · ${t("feedback.artifact.subtitle")}`}
        action={
          <Button onClick={download}>
            <Download className="h-3.5 w-3.5" />
            {t("feedback.artifact.download")}
          </Button>
        }
      />
      {artifact.kind === "json" && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-sky-50 px-3 py-2 text-2xs text-sky-800">
          <FileJson className="h-3.5 w-3.5" />
          {t("feedback.artifact.machineReadable")}
        </div>
      )}
      {artifact.kind === "markdown" ? (
        <div className="overflow-x-auto">
          <div className={markdownStyles}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{payload.content}</ReactMarkdown>
          </div>
        </div>
      ) : (
        <pre className="max-h-[620px] overflow-auto rounded-lg bg-slate-950 p-4 font-mono text-2xs leading-relaxed text-slate-200">
          {pretty}
        </pre>
      )}
    </Card>
  );
}
