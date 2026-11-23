import { describe, expect, it, vi } from "vitest";
import commonEn from "../locales/en.json";
import commonFr from "../locales/fr.json";
import appEn from "../locales/en/app.json";
import appFr from "../locales/fr/app.json";
import homeEn from "../locales/en/home.json";
import homeFr from "../locales/fr/home.json";
import formsEn from "../locales/en/forms.json";
import formsFr from "../locales/fr/forms.json";
import viewsEn from "../locales/en/views.json";
import viewsFr from "../locales/fr/views.json";
import modalsEn from "../locales/en/modals.json";
import modalsFr from "../locales/fr/modals.json";
import feedbackEn from "../locales/en/feedback.json";
import feedbackFr from "../locales/fr/feedback.json";

type Resource = Record<string, string>;

const bundles: Record<string, [Resource, Resource]> = {
  common: [commonEn as Resource, commonFr as Resource],
  app: [appEn as Resource, appFr as Resource],
  home: [homeEn as Resource, homeFr as Resource],
  forms: [formsEn as Resource, formsFr as Resource],
  views: [viewsEn as Resource, viewsFr as Resource],
  modals: [modalsEn as Resource, modalsFr as Resource],
  feedback: [feedbackEn as Resource, feedbackFr as Resource],
};

function placeholders(value: string): string[] {
  return [...value.matchAll(/{{\s*([^}\s]+)/g)].map((match) => match[1]).sort();
}

describe("locale resources", () => {
  it.each(Object.entries(bundles))("%s bundles stay in English/French parity", (_name, [en, fr]) => {
    expect(Object.keys(fr).sort()).toEqual(Object.keys(en).sort());

    for (const key of Object.keys(en)) {
      expect(fr[key]).not.toBe("");
      expect(placeholders(fr[key])).toEqual(placeholders(en[key]));
    }
  });
});

describe("i18n bootstrap", () => {
  it("uses the stored locale for UI strings and document metadata", async () => {
    vi.resetModules();
    window.localStorage.setItem("fortcloud.locale", "fr");
    document.head.innerHTML = '<meta name="description" content="" />';

    const i18n = (await import("../i18n")).default;

    expect(i18n.language).toBe("fr");
    expect(i18n.t("app.tabs.outputs")).toBe("Sorties");
    expect(document.documentElement.lang).toBe("fr");
    expect(document.title).toBe("Console FortCloud");
    expect(document.querySelector('meta[name="description"]')?.getAttribute("content")).toContain(
      "une interface unique et apaisée",
    );

    await i18n.changeLanguage("en");

    expect(i18n.t("app.tabs.outputs")).toBe("Outputs");
    expect(document.documentElement.lang).toBe("en");
    expect(document.title).toBe("FortCloud Console");
  });
});
