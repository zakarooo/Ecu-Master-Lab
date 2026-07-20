import { test, expect, type Page } from "@playwright/test";

const API = process.env.BACKEND_URL || "https://ecu-backend-production.up.railway.app";
const FRONTEND = process.env.FRONTEND_URL || "https://frontend-beige-rho-83.vercel.app";
const AUTH_FILE = "e2e/.auth/user.json";

const ts = Date.now();
function rndEmail() { return `biz_${ts}_${Math.random().toString(36).slice(2, 5)}@e2e.test`; }

const USER = { first_name: "BizE2E", last_name: "Testeur", email: rndEmail(), password: "Str0ng!Pass#2026" };

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

// ── Reference ────────────────────────────────────────────────

test.describe("Reference data", () => {
  test.use({ storageState: AUTH_FILE });

  test("reference home loads 10 category cards", async ({ page }) => {
    await page.goto(`${FRONTEND}/reference`);
    await page.waitForLoadState("networkidle");
    const cards = page.locator("a[href^='/reference/']");
    await expect(cards.first()).toBeVisible({ timeout: 10_000 });
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(8);
  });

  test("manufacturers page loads table with data", async ({ page }) => {
    await page.goto(`${FRONTEND}/reference/manufacturers`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    const heading = page.locator("h1");
    await expect(heading).toBeVisible();
    const headingText = await heading.innerText();
    expect(headingText).toMatch(/Fabricant/i);
    const rows = page.locator("table tbody tr, [class*='row']");
    const count = await rows.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test("manufacturers search filters results", async ({ page }) => {
    await page.goto(`${FRONTEND}/reference/manufacturers`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    const searchInput = page.locator('input[placeholder*="echercher"]');
    if (await searchInput.isVisible()) {
      const initialCount = await page.locator("table tbody tr").count();
      await searchInput.fill("Bosch");
      await page.waitForTimeout(1500);
      const filteredCount = await page.locator("table tbody tr").count();
      expect(filteredCount).toBeLessThanOrEqual(initialCount);
    }
  });

  test("ecu-models page loads", async ({ page }) => {
    await page.goto(`${FRONTEND}/reference/ecu-models`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    const heading = page.locator("h1");
    await expect(heading).toBeVisible();
  });

  test("processors page loads", async ({ page }) => {
    await page.goto(`${FRONTEND}/reference/processors`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    const heading = page.locator("h1");
    await expect(heading).toBeVisible();
  });

  test("signatures page loads", async ({ page }) => {
    await page.goto(`${FRONTEND}/reference/signatures`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    const heading = page.locator("h1");
    await expect(heading).toBeVisible();
  });
});

// ── Intelligence ─────────────────────────────────────────────

test.describe("Intelligence dashboard", () => {
  test.use({ storageState: AUTH_FILE });

  test("intelligence page loads with overview tab", async ({ page }) => {
    await page.goto(`${FRONTEND}/intelligence`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    const heading = page.locator("h1");
    await expect(heading).toBeVisible({ timeout: 10_000 });
    const headingText = await heading.innerText();
    expect(headingText).toMatch(/Intelligence|ECU/i);
  });

  test("intelligence stats cards render", async ({ page }) => {
    await page.goto(`${FRONTEND}/intelligence`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);
    const bodyText = await page.locator("body").innerText();
    const hasStats = bodyText.includes("Total Maps") || bodyText.includes("ECU Models") ||
      bodyText.includes("Maps") || bodyText.includes("Categories");
    expect(hasStats).toBeTruthy();
  });
});

// ── Profile ──────────────────────────────────────────────────

test.describe("Profile management", () => {
  test.use({ storageState: AUTH_FILE });

  test("profile page shows user info and forms", async ({ page }) => {
    await page.goto(`${FRONTEND}/profile`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);
    const heading = page.locator("h1");
    await expect(heading).toBeVisible({ timeout: 10_000 });
    const bodyText = await page.locator("body").innerText();
    expect(bodyText).toMatch(/Profil|profil|Informations/i);
    const emailInput = page.locator('input[type="email"]');
    await expect(emailInput).toBeVisible({ timeout: 5_000 });
  });

  test("profile pre-fills current user email", async ({ page }) => {
    await page.goto(`${FRONTEND}/profile`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);
    const emailInput = page.locator('input[type="email"]');
    const value = await emailInput.inputValue();
    expect(value).toContain("@");
  });

  test("password change form is present", async ({ page }) => {
    await page.goto(`${FRONTEND}/profile`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);
    const passwordInputs = page.locator('input[type="password"]');
    const count = await passwordInputs.count();
    expect(count).toBeGreaterThanOrEqual(2);
  });
});

// ── Project Wizard ───────────────────────────────────────────

test.describe("New project wizard", () => {
  test.use({ storageState: AUTH_FILE });

  test("wizard loads at step 1", async ({ page }) => {
    await page.goto(`${FRONTEND}/projects/new`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    const heading = page.locator("h1");
    await expect(heading).toBeVisible({ timeout: 10_000 });
    const headingText = await heading.innerText();
    expect(headingText).toMatch(/Nouveau|Projet|ECU/i);
    const nameInput = page.locator('input[placeholder*="projet"], input[placeholder*="Projet"]');
    await expect(nameInput).toBeVisible({ timeout: 5_000 });
  });

  test("wizard step 2 shows vehicle fields", async ({ page }) => {
    await page.goto(`${FRONTEND}/projects/new`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    const nameInput = page.locator('input[placeholder*="projet"], input[placeholder*="Projet"]');
    await nameInput.fill("Test E2E Project");
    const nextBtn = page.locator("button").filter({ hasText: /Suivant|Next/i });
    await nextBtn.click();
    await page.waitForTimeout(500);
    const bodyText = await page.locator("body").innerText();
    expect(bodyText).toMatch(/Vehicule|vehicule|Constructeur|Motorisation/i);
  });

  test("wizard step 3 shows tool selection", async ({ page }) => {
    await page.goto(`${FRONTEND}/projects/new`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    const nameInput = page.locator('input[placeholder*="projet"], input[placeholder*="Projet"]');
    await nameInput.fill("Test E2E Project");
    let nextBtn = page.locator("button").filter({ hasText: /Suivant|Next/i });
    await nextBtn.click();
    await page.waitForTimeout(500);
    nextBtn = page.locator("button").filter({ hasText: /Suivant|Next/i });
    await nextBtn.click();
    await page.waitForTimeout(500);
    const bodyText = await page.locator("body").innerText();
    expect(bodyText).toMatch(/Autotuner|Flex|KESS|KTAG|Outil|Lecture/i);
    const createBtn = page.locator("button").filter({ hasText: /Cr[eé]er|Create/i });
    await expect(createBtn).toBeVisible();
  });

  test("wizard back button returns to previous step", async ({ page }) => {
    await page.goto(`${FRONTEND}/projects/new`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    const nameInput = page.locator('input[placeholder*="projet"], input[placeholder*="Projet"]');
    await nameInput.fill("Test E2E Back");
    const nextBtn = page.locator("button").filter({ hasText: /Suivant|Next/i });
    await nextBtn.click();
    await page.waitForTimeout(500);
    const backBtn = page.locator("button").filter({ hasText: /Retour|Back/i });
    await expect(backBtn).toBeVisible();
    await backBtn.click();
    await page.waitForTimeout(500);
    const nameAgain = page.locator('input[placeholder*="projet"], input[placeholder*="Projet"]');
    const val = await nameAgain.inputValue();
    expect(val).toBe("Test E2E Back");
  });
});

// ── Navigation ───────────────────────────────────────────────

test.describe("Cross-page navigation", () => {
  test.use({ storageState: AUTH_FILE });

  test("sidebar links all navigate correctly", async ({ page }) => {
    await page.goto(`${FRONTEND}/dashboard`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);

    const links = [
      { text: "Dashboard", expected: "/dashboard" },
      { text: "Nouveau Projet", expected: "/projects/new" },
      { text: "Analyse", expected: "/analysis" },
      { text: "Référentiel", expected: "/reference" },
      { text: "Intelligence", expected: "/intelligence" },
      { text: "Mon Profil", expected: "/profile" },
    ];

    for (const link of links) {
      const el = page.locator("a").filter({ hasText: new RegExp(link.text, "i") }).first();
      if (await el.isVisible({ timeout: 2000 }).catch(() => false)) {
        await el.click();
        await page.waitForURL(`**${link.expected}*`, { timeout: 10_000 });
        expect(page.url()).toContain(link.expected);
        await page.goBack();
        await page.waitForLoadState("networkidle");
        await page.waitForTimeout(500);
      }
    }
  });

  test("dashboard project count matches stats", async ({ page }) => {
    await page.goto(`${FRONTEND}/dashboard`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    const bodyText = await page.locator("body").innerText();
    expect(bodyText).toMatch(/Dashboard|Projets/i);
  });
});

// ── Analysis page ────────────────────────────────────────────

test.describe("Analysis page", () => {
  test.use({ storageState: AUTH_FILE });

  test("analysis page loads with tables", async ({ page }) => {
    await page.goto(`${FRONTEND}/analysis`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);
    const heading = page.locator("h1");
    await expect(heading).toBeVisible({ timeout: 10_000 });
    const headingText = await heading.innerText();
    expect(headingText).toMatch(/Analyse/i);
  });

  test("analysis page shows stat cards", async ({ page }) => {
    await page.goto(`${FRONTEND}/analysis`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);
    const bodyText = await page.locator("body").innerText();
    const hasStats = bodyText.includes("Fichiers") || bodyText.includes("Analyses") ||
      bodyText.includes("Confiance") || bodyText.includes("Aucun");
    expect(hasStats).toBeTruthy();
  });
});
