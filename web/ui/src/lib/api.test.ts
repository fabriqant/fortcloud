import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { api } from "./api";

const fetchMock = vi.fn();

function lastCall(): [string, RequestInit] {
  return fetchMock.mock.calls[fetchMock.mock.calls.length - 1] as [string, RequestInit];
}

function headers(init: RequestInit): Record<string, string> {
  return init.headers as Record<string, string>;
}

describe("API requests", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", fetchMock);
    fetchMock.mockReset();
    fetchMock.mockResolvedValue({
      ok: true,
      statusText: "OK",
      json: async () => ({ ok: true }),
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends the stored locale and no credentials on every request", async () => {
    window.localStorage.setItem("fortcloud.locale", "fr");

    await api.tools();

    const [url, init] = lastCall();
    expect(url).toBe("/api/tools");
    expect(headers(init)).toMatchObject({
      "Content-Type": "application/json",
      "Accept-Language": "fr",
    });
    expect(headers(init)).not.toHaveProperty("Authorization");
    expect(headers(init)).not.toHaveProperty("Cookie");
  });

  it("sends only non-secret connector identifiers", async () => {
    await api.runConnector({ profile: "my-profile", region: "eu-west-1" });

    const [, init] = lastCall();
    expect(JSON.parse(init.body as string)).toEqual({
      profile: "my-profile",
      region: "eu-west-1",
    });
    expect(init.body as string).not.toMatch(/secret|password|credential/i);
  });

  it("surfaces translated server error details", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      statusText: "Not Found",
      json: async () => ({ detail: "Artefact non généré : missing.md" }),
    });

    await expect(api.artifact("atlas", "missing.md")).rejects.toThrow(
      "Artefact non généré : missing.md",
    );
  });
});
