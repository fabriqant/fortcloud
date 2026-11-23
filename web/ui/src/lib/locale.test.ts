import { beforeEach, describe, expect, it, vi } from "vitest";
import { getLocale, setLocale } from "./locale";

const reloadPage = vi.hoisted(() => vi.fn());

vi.mock("./page", () => ({ reloadPage }));

describe("locale persistence", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("defaults to English when nothing is stored", () => {
    expect(getLocale()).toBe("en");
  });

  it("only accepts French as the alternative locale", () => {
    window.localStorage.setItem("fortcloud.locale", "fr");
    expect(getLocale()).toBe("fr");

    window.localStorage.setItem("fortcloud.locale", "de");
    expect(getLocale()).toBe("en");
  });

  it("stores the locale and reloads so server metadata follows", () => {
    setLocale("fr");

    expect(window.localStorage.getItem("fortcloud.locale")).toBe("fr");
    expect(reloadPage).toHaveBeenCalledOnce();
  });
});
