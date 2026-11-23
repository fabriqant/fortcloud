import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import { getLocale } from "./lib/locale";
import commonEn from "./locales/en.json";
import commonFr from "./locales/fr.json";
import appEn from "./locales/en/app.json";
import appFr from "./locales/fr/app.json";
import homeEn from "./locales/en/home.json";
import homeFr from "./locales/fr/home.json";
import formsEn from "./locales/en/forms.json";
import formsFr from "./locales/fr/forms.json";
import viewsEn from "./locales/en/views.json";
import viewsFr from "./locales/fr/views.json";
import modalsEn from "./locales/en/modals.json";
import modalsFr from "./locales/fr/modals.json";
import feedbackEn from "./locales/en/feedback.json";
import feedbackFr from "./locales/fr/feedback.json";

i18n.use(initReactI18next).init({
  resources: {
    en: {
      translation: {
        ...commonEn,
        ...appEn,
        ...homeEn,
        ...formsEn,
        ...viewsEn,
        ...modalsEn,
        ...feedbackEn,
      },
    },
    fr: {
      translation: {
        ...commonFr,
        ...appFr,
        ...homeFr,
        ...formsFr,
        ...viewsFr,
        ...modalsFr,
        ...feedbackFr,
      },
    },
  },
  lng: getLocale(),
  fallbackLng: "en",
  keySeparator: false,
  nsSeparator: false,
  interpolation: { escapeValue: false },
});

export function applyLocaleMetadata(locale: string): void {
  const french = locale === "fr";
  document.documentElement.lang = french ? "fr" : "en";
  document.title = french ? "Console FortCloud" : "FortCloud Console";
  const description = document.querySelector('meta[name="description"]');
  description?.setAttribute(
    "content",
    french
      ? "Console FortCloud - une interface unique et apaisée pour les sept outils FortCloud de résilience cloud."
      : "FortCloud Console - a single, calm interface for the seven FortCloud cloud resilience tools.",
  );
}

applyLocaleMetadata(i18n.language);
i18n.on("languageChanged", applyLocaleMetadata);

export default i18n;
