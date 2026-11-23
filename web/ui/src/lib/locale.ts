import { reloadPage } from "./page";

export type Locale = "en" | "fr";

const LOCALE_KEY = "fortcloud.locale";

export function getLocale(): Locale {
  try {
    const stored = window.localStorage.getItem(LOCALE_KEY);
    return stored === "fr" ? "fr" : "en";
  } catch {
    return "en";
  }
}

export function setLocale(locale: Locale): void {
  try {
    window.localStorage.setItem(LOCALE_KEY, locale);
  } catch {
    // The page still switches language for this session.
  }
  // Metadata is translated server-side, so a reload keeps every view consistent.
  reloadPage();
}
