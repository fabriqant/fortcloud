import { useMemo, useRef } from "react";
import { Save } from "lucide-react";
import { Badge, Button, Card } from "./ui";

export function ModelEditor({
  file,
  value,
  dirty,
  saving,
  onChange,
  onSave,
}: {
  file: string;
  value: string;
  dirty: boolean;
  saving: boolean;
  onChange: (value: string) => void;
  onSave: () => void;
}) {
  const gutter = useRef<HTMLDivElement>(null);
  const lineCount = useMemo(() => Math.max(1, value.split("\n").length), [value]);

  return (
    <Card padded={false} className="overflow-hidden">
      <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3">
        <div className="flex items-center gap-3">
          <span className="font-mono text-xs font-semibold text-slate-800">{file}</span>
          {dirty ? <Badge tone="amber">Unsaved</Badge> : <Badge tone="green">Saved</Badge>}
        </div>
        <Button variant="primary" onClick={onSave} disabled={!dirty} loading={saving}>
          <Save className="h-3.5 w-3.5" />
          Save model
        </Button>
      </div>
      <div className="flex h-[560px] bg-slate-950 text-slate-100">
        <div
          ref={gutter}
          className="w-14 shrink-0 select-none overflow-hidden border-r border-slate-800 bg-slate-900/60 py-4 text-right font-mono text-xs leading-6 text-slate-600"
        >
          {Array.from({ length: lineCount }, (_, index) => (
            <div key={index} className="pr-3">
              {index + 1}
            </div>
          ))}
        </div>
        <textarea
          value={value}
          spellCheck={false}
          onChange={(event) => onChange(event.target.value)}
          onScroll={(event) => {
            if (gutter.current) gutter.current.scrollTop = event.currentTarget.scrollTop;
          }}
          className="h-full flex-1 resize-none bg-transparent py-4 pl-4 pr-6 font-mono text-xs leading-6 text-slate-100 outline-none"
        />
      </div>
      <p className="border-t border-slate-100 px-5 py-3 text-2xs text-slate-500">
        YAML is the source of truth. Generated artifacts are rebuilt by <span className="font-mono">Check</span>.
      </p>
    </Card>
  );
}
