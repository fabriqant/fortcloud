import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ToolSidebar } from "../components/ToolSidebar";
import i18n from "../i18n";
import type { ToolInfo } from "../lib/types";

const reloadPage = vi.hoisted(() => vi.fn());

vi.mock("../lib/page", () => ({ reloadPage }));

const tools: ToolInfo[] = [
  ["atlas", "Atlas"],
  ["failover", "Failover"],
  ["ark", "Ark"],
  ["ballast", "Ballast"],
  ["vitals", "Vitals"],
  ["custodian", "Custodian"],
  ["crucible", "Crucible"],
].map(([id, name]) => ({
  id,
  name: `FortCloud ${name}`,
  tagline: `${name} tagline`,
  description: `${name} description`,
  accent: "blue",
  icon: "activity",
  artifacts: [],
}));

function renderSidebar() {
  return render(
    <ToolSidebar
      tools={tools}
      activeId="atlas"
      home={false}
      version="0.1.0"
      onHome={() => undefined}
      onSelect={() => undefined}
    />,
  );
}

describe("ToolSidebar", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("en");
  });

  it("keeps the seven tools in their fixed order", () => {
    renderSidebar();

    const shortNames = tools.map((tool) => tool.name.replace(/^FortCloud\s+/, ""));
    const labels = screen
      .getAllByRole("button")
      .map((button) => button.textContent ?? "")
      .filter((text) => shortNames.some((name) => text.includes(name)));
    const orderedNames = labels.map(
      (text) => shortNames.find((name) => text.startsWith(name)) ?? "",
    );

    expect(orderedNames).toEqual(shortNames);
    expect(screen.getByText("Language")).toBeInTheDocument();
  });

  it("translates the footer and persists a locale change", async () => {
    vi.clearAllMocks();
    await i18n.changeLanguage("fr");
    renderSidebar();

    expect(screen.getByText("Langue")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "fr" })).toHaveAttribute("aria-pressed", "true");

    fireEvent.click(screen.getByRole("button", { name: "en" }));

    expect(window.localStorage.getItem("fortcloud.locale")).toBe("en");
    expect(reloadPage).toHaveBeenCalledOnce();
  });
});
