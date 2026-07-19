import { test, expect, type Page } from "@playwright/test";

const API = process.env.BACKEND_URL || "https://ecu-backend-production.up.railway.app";
const FRONTEND = process.env.FRONTEND_URL || "https://frontend-beige-rho-83.vercel.app";
const AUTH_FILE = "e2e/.auth/user.json";

const ts = Date.now();
function rndEmail() { return `test_${ts}_${Math.random().toString(36).slice(2, 5)}@e2e.test`; }

const USER = { first_name: "E2E", last_name: "Test", email: rndEmail(), password: "Str0ng!Pass#2026" };

async function setupAuth(request: any, page: Page) {
  const r = await request.post(`${API}/api/auth/register`, {
    data: { first_name: USER.first_name, last_name: USER.last_name, email: USER.email, password: USER.password },
  });
  expect(r.ok(), `register failed: ${r.status()} ${await r.text()}`).toBeTruthy();
  const data = await r.json();

  await page.goto(FRONTEND);
  await page.evaluate(({ token, user }) => {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
    document.cookie = `session=${token}; path=/; max-age=86400; SameSite=Lax`;
  }, { token: data.access_token, user: data.user });

  await page.context().storageState({ path: AUTH_FILE });
}

test.beforeAll(async ({ request, browser }) => {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await setupAuth(request, page);
  await page.close();
  await ctx.close();
});

test("API health", async ({ request }) => {
  const r = await request.get(`${API}/api/health`);
  expect(r.ok()).toBeTruthy();
  const b = await r.json();
  expect(b.status).toBe("healthy");
});

test("dashboard redirects to /login when unauthenticated", async ({ page }) => {
  await page.goto(`${FRONTEND}/dashboard`);
  await page.waitForURL("**/login", { timeout: 10_000 });
  expect(page.url()).toContain("/login");
});

test("admin redirects to /login when unauthenticated", async ({ page }) => {
  await page.goto(`${FRONTEND}/admin`);
  await page.waitForURL("**/login", { timeout: 10_000 });
  expect(page.url()).toContain("/login");
});

test.describe("authenticated", () => {
  test.use({ storageState: AUTH_FILE });

  test("dashboard loads with sidebar", async ({ page }) => {
    await page.goto(`${FRONTEND}/dashboard`);
    await page.waitForLoadState("networkidle");
    await expect(page.locator("a").filter({ hasText: "Dashboard" }).first()).toBeVisible();
    await expect(page.locator("a").filter({ hasText: "Nouveau Projet" }).first()).toBeVisible();
    await expect(page.locator("a").filter({ hasText: "Mon Profil" }).first()).toBeVisible();
  });

  test("clicking Mon Profil → /profile", async ({ page }) => {
    await page.goto(`${FRONTEND}/dashboard`);
    await page.waitForLoadState("networkidle");
    await page.locator("a").filter({ hasText: "Mon Profil" }).first().click();
    await page.waitForURL("**/profile", { timeout: 10_000 });
    expect(page.url()).toContain("/profile");
  });

  test("profile shows email and can update name", async ({ page }) => {
    await page.goto(`${FRONTEND}/profile`);
    await page.waitForLoadState("networkidle");
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toHaveValue(USER.email, { timeout: 10_000 });
    const firstNameInput = page.locator('input[type="text"]').first();
    await firstNameInput.clear();
    await firstNameInput.fill("E2E Updated");
    await page.locator('button:has-text("Enregistrer")').click();
    await expect(page.locator("text=Profil mis à jour")).toBeVisible({ timeout: 10_000 });
  });

  test("reference page loads cards", async ({ page }) => {
    await page.goto(`${FRONTEND}/reference`);
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h3").filter({ hasText: "Fabricants" }).first()).toBeVisible();
    await expect(page.locator("h3").filter({ hasText: "Modèles ECU" }).first()).toBeVisible();
  });

  test("clicking Fabricants → /reference/manufacturers", async ({ page }) => {
    await page.goto(`${FRONTEND}/reference`);
    await page.waitForLoadState("networkidle");
    await page.locator("a[href='/reference/manufacturers']").first().click();
    await page.waitForURL("**/reference/manufacturers", { timeout: 10_000 });
    expect(page.url()).toContain("/reference/manufacturers");
  });

  test("logout clears token and redirects", async ({ page }) => {
    await page.goto(`${FRONTEND}/dashboard`);
    await page.waitForLoadState("networkidle");
    await page.locator("button, a").filter({ hasText: /Déconnexion/i }).first().click();
    await page.waitForTimeout(2000);
    const token = await page.evaluate(() => localStorage.getItem("token"));
    expect(token).toBeNull();
  });
});

test("login with wrong password shows error", async ({ page }) => {
  await page.goto(`${FRONTEND}/login`);
  await page.locator('input[type="email"]').fill(USER.email);
  await page.locator('input[type="password"]').fill("BadPass!123");
  await page.locator('button[type="submit"]').click();
  await page.waitForTimeout(3000);
  const bodyText = await page.locator("body").innerText();
  expect(bodyText).toMatch(/incorrect|Erreur|erreur|mot de passe/i);
});
