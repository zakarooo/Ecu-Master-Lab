import { test, expect } from "@playwright/test";

test.describe("Page Entreprise B2B", () => {
  test("affiche le contenu principal", async ({ page }) => {
    await page.goto("/entreprise");
    await expect(page).toHaveTitle(/entreprise/i);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  });

  test("affiche les fonctionnalités B2B", async ({ page }) => {
    await page.goto("/entreprise");
    await expect(page.getByText(/batch|masse|multi/i)).toBeVisible();
  });

  test("bouton CTA visible", async ({ page }) => {
    await page.goto("/entreprise");
    const cta = page.getByRole("link", { name: /dossier salarié/i });
    await expect(cta).toBeVisible();
  });

  test("retour à l'accueil via le header", async ({ page }) => {
    await page.goto("/entreprise");
    await page.getByRole("link", { name: "DroitSéjour" }).first().click();
    await expect(page).toHaveURL("/");
  });
});
