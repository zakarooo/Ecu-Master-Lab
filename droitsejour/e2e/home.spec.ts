import { test, expect } from "@playwright/test";

test.describe("Page d'accueil", () => {
  test("affiche le hero et la navigation", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/DroitSéjour/);
    await expect(page.locator("h1")).toContainText("séjour en France");
    await expect(page.getByRole("link", { name: "Créer mon dossier" })).toBeVisible();
  });

  test("la section features est visible", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Fonctionnalités principales")).toBeVisible();
    await expect(page.getByText("Analyse IA")).toBeVisible();
    await expect(page.getByText("Courriers automatiques")).toBeVisible();
  });

  test("la section 'Comment ça marche' est visible", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Comment ça marche")).toBeVisible();
  });

  test("le disclaimer juridique est présent", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Avertissement :")).toBeVisible();
  });

  test("navigation vers la page entreprise via le header", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Entreprise" }).click();
    await expect(page).toHaveURL(/\/entreprise/);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  });

  test("navigation vers la création de dossier", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("link", { name: "Créer mon dossier" }).click();
    await expect(page).toHaveURL(/\/dossier\/new/);
    await expect(page.getByText("Création du dossier")).toBeVisible();
  });
});
