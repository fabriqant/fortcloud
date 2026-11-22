import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const ACCENT: Record<string, { bar: string; dot: string; soft: string; text: string }> = {
  red: { bar: "bg-rose-500", dot: "bg-rose-500", soft: "bg-rose-50", text: "text-rose-700" },
  orange: { bar: "bg-orange-500", dot: "bg-orange-500", soft: "bg-orange-50", text: "text-orange-700" },
  amber: { bar: "bg-amber-500", dot: "bg-amber-500", soft: "bg-amber-50", text: "text-amber-700" },
  blue: { bar: "bg-sky-500", dot: "bg-sky-500", soft: "bg-sky-50", text: "text-sky-700" },
  green: { bar: "bg-emerald-500", dot: "bg-emerald-500", soft: "bg-emerald-50", text: "text-emerald-700" },
  violet: { bar: "bg-violet-500", dot: "bg-violet-500", soft: "bg-violet-50", text: "text-violet-700" },
  pink: { bar: "bg-pink-500", dot: "bg-pink-500", soft: "bg-pink-50", text: "text-pink-700" },
};

export function accentFor(name: string) {
  return ACCENT[name] ?? ACCENT.blue;
}

export function displayToolName(name: string) {
  return name.replace(/^Fortcloud\s+/i, "");
}
