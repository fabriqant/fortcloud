import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ImportView } from "../components/ImportView";
import i18n from "../i18n";

const mocks = vi.hoisted(() => ({
  imports: vi.fn(),
  importDiff: vi.fn(),
  stageImport: vi.fn(),
  acceptImport: vi.fn(),
  discardImport: vi.fn(),
}));

vi.mock("../lib/api", () => ({ api: mocks }));

const proposal = "version: 1\ncomponents:\n  - id: new-component\n";
const diff = {
  file: "components.yaml",
  changed: true,
  current: "version: 1\ncomponents: []\n",
  proposed: proposal,
  diff: "--- current\n+++ proposed\n@@\n+  - id: new-component",
};

function renderImportView(onAccepted = vi.fn()) {
  render(
    <ImportView toolId="atlas" files={["components.yaml"]} onAccepted={onAccepted} />,
  );
  return onAccepted;
}

async function stageProposal() {
  fireEvent.change(screen.getByPlaceholderText(/version: 1/), { target: { value: proposal } });
  fireEvent.click(screen.getByRole("button", { name: "Déposer la proposition" }));
  await waitFor(() => {
    expect(screen.getByText(/déposé\. Examinez le diff avant de l'accepter/)).toBeInTheDocument();
  });
}

describe("ImportView", () => {
  beforeEach(async () => {
    await i18n.changeLanguage("fr");
    vi.clearAllMocks();
    mocks.imports.mockResolvedValueOnce([]).mockResolvedValue([
      { name: "components.yaml", size: proposal.length },
    ]);
    mocks.importDiff.mockResolvedValue(diff);
    mocks.stageImport.mockResolvedValue({ ok: true });
    mocks.acceptImport.mockResolvedValue({ ok: true });
    mocks.discardImport.mockResolvedValue({ ok: true });
  });

  it("requires a diff review before applying a proposal", async () => {
    const onAccepted = renderImportView();

    await stageProposal();

    expect(mocks.stageImport).toHaveBeenCalledWith("atlas", "components.yaml", proposal);
    expect(mocks.acceptImport).not.toHaveBeenCalled();
    expect(screen.getByText("Vérifiez chaque ligne avant d'accepter.")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Accepter" })).toBeEnabled();
    });
    fireEvent.click(screen.getByRole("button", { name: "Accepter" }));

    await waitFor(() => {
      expect(mocks.acceptImport).toHaveBeenCalledWith("atlas", "components.yaml");
    });
    expect(onAccepted).toHaveBeenCalledOnce();
    expect(screen.getByText(/appliqué au modèle de l'espace de travail/)).toBeInTheDocument();
  });

  it("discards a staged proposal without applying it", async () => {
    renderImportView();

    await stageProposal();
    fireEvent.click(screen.getByRole("button", { name: "Rejeter" }));

    await waitFor(() => {
      expect(mocks.discardImport).toHaveBeenCalledWith("atlas", "components.yaml");
    });
    expect(mocks.acceptImport).not.toHaveBeenCalled();
    expect(screen.getByText("components.yaml rejeté.")).toBeInTheDocument();
  });
});
