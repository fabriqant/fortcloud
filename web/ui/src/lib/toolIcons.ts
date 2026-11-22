import {
  Activity,
  Archive,
  Boxes,
  FlaskConical,
  Gauge,
  Network,
  ShieldCheck,
  Shuffle,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export const TOOL_ICONS: Record<string, LucideIcon> = {
  network: Network,
  shuffle: Shuffle,
  archive: Archive,
  gauge: Gauge,
  activity: Activity,
  shield: ShieldCheck,
  flask: FlaskConical,
};

export function toolIcon(name: string | undefined): LucideIcon {
  return (name && TOOL_ICONS[name]) || Boxes;
}
