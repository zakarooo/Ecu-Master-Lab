import { defineConfig, devices } from "@playwright/test";

const API_BASE = process.env.BACKEND_URL || "https://ecu-backend-production.up.railway.app";
const FRONTEND_BASE = process.env.FRONTEND_URL || "https://frontend-beige-rho-83.vercel.app";

export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  retries: 1,
  reporter: "list",
  use: {
    baseURL: FRONTEND_BASE,
    screenshot: "only-on-failure",
    trace: "on-first-retry",
    headless: true,
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
  ],
  globalSetup: undefined,
});
