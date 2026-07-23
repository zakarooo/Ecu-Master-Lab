import { test, expect } from "@playwright/test";

test.describe("SEO & Métadonnées", () => {
  test("homepage a un title et description valides", async ({ page }) => {
    await page.goto("/");
    const title = await page.title();
    expect(title.length).toBeGreaterThan(5);
    const meta = await page.locator('meta[name="description"]').getAttribute("content");
    expect(meta?.length).toBeGreaterThan(20);
  });

  test("la page entreprise a des métadonnées", async ({ page }) => {
    await page.goto("/entreprise");
    const title = await page.title();
    expect(title.length).toBeGreaterThan(5);
  });

  test("JSON-LD organization est présent", async ({ page }) => {
    await page.goto("/");
    const scripts = page.locator('script[type="application/ld+json"]');
    const count = await scripts.count();
    expect(count).toBeGreaterThanOrEqual(1);
    const text = await scripts.first().textContent();
    expect(text).toBeTruthy();
    const data = JSON.parse(text!);
    expect(data["@type"]).toBeDefined();
  });

  test("sitemap.xml est accessible", async ({ request }) => {
    const res = await request.get("/sitemap.xml");
    expect(res.status()).toBe(200);
    const body = await res.text();
    expect(body).toContain("urlset");
  });

  test("robots.txt est accessible", async ({ request }) => {
    const res = await request.get("/robots.txt");
    expect(res.status()).toBe(200);
    const body = await res.text();
    expect(body).toContain("User-Agent");
  });

  test("la page 404 fonctionne", async ({ page }) => {
    const res = await page.goto("/page-inexistante-12345");
    expect(res?.status()).toBe(404);
    await expect(page.getByText(/trouvée|not found/i)).toBeVisible();
  });
});
