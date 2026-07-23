import { test, expect } from "@playwright/test";

test.describe("Wizard Flow", () => {
  test("ouvre le wizard et affiche l'étape 1", async ({ page }) => {
    await page.goto("/dossier/new");
    await expect(page.getByText("Création du dossier")).toBeVisible();
    await expect(page.getByRole("button", { name: "Informations personnelles" })).toBeVisible();
  });

  test("step 1: affiche le formulaire personnel", async ({ page }) => {
    await page.goto("/dossier/new");
    await expect(page.getByLabel(/nom/i).first()).toBeVisible();
    await expect(page.getByLabel(/prénom/i).first()).toBeVisible();
    await expect(page.getByLabel(/date de naissance/i).first()).toBeVisible();
    await expect(page.getByLabel(/email/i).first()).toBeVisible();
  });

  test("step 1: remplit les champs et avance", async ({ page }) => {
    await page.goto("/dossier/new");
    await page.getByLabel(/nom/i).first().fill("Dupont");
    await page.getByLabel(/prénom/i).first().fill("Marie");
    await page.getByLabel(/date de naissance/i).first().fill("1990-05-15");
    await page.getByLabel(/lieu de naissance/i).first().fill("Paris");
    await page.getByLabel(/adresse/i).first().fill("10 rue de la Paix");
    await page.getByLabel(/code postal/i).first().fill("75002");
    await page.getByLabel(/ville/i).first().fill("Paris");
    await page.getByLabel(/téléphone/i).first().fill("0612345678");
    await page.getByLabel(/email/i).first().fill("marie@test.fr");

    await page.getByRole("button", { name: /suivant/i }).click();

    await expect(page.getByRole("button", { name: "Situation administrative" })).toBeVisible({ timeout: 15000 });
  });

  test("theme toggle fonctionne", async ({ page }) => {
    await page.goto("/");
    const themeBtn = page.getByRole("button", { name: /basculer le thème/i });
    await expect(themeBtn).toBeVisible();

    await themeBtn.click();
    const isDark = await page.evaluate(() => document.documentElement.classList.contains("dark"));
    expect(isDark).toBe(true);

    await themeBtn.click();
    const isLight = await page.evaluate(() => !document.documentElement.classList.contains("dark"));
    expect(isLight).toBe(true);
  });

  test("mobile menu toggle fonctionne", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/");

    const menuBtn = page.getByRole("button", { name: /ouvrir le menu/i });
    await expect(menuBtn).toBeVisible();
    await menuBtn.click();

    await expect(page.getByRole("link", { name: "Entreprise" })).toBeVisible();
  });

  test("un dossier créé via API est accessible dans le wizard", async ({ request, page }) => {
    const res = await request.post("/api/dossiers", {
      data: {
        nom: "Test Wizard",
        statut: "brouillon",
        informationsPersonnelles: {
          nom: "Dupont",
          prenom: "Marie",
          dateNaissance: "1990-05-15",
          lieuNaissance: "Paris",
          nationalite: "Sénégal",
          adresse: "10 rue de la Paix",
          codePostal: "75002",
          ville: "Paris",
          telephone: "0612345678",
          email: "marie@test.fr",
          situationFamiliale: "celibataire",
          nombreEnfants: 0,
        },
        situationAdministrative: { statutSejour: "irregulier" },
        situationFamiliale: { situation: "celibataire" },
        demarchesPrecedentes: [],
        documents: [],
        memos: [],
        courriers: [],
        checklist: [],
        rapportGenere: false,
      },
    });
    const dossier = await res.json();

    await page.goto(`/dossier/${dossier.id}`);
    await expect(page.getByText(/Dupont|Marie/)).toBeVisible({ timeout: 15000 });
  });
});
