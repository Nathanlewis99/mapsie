import { defineConfig, devices } from "@playwright/test";

// End-to-end tests: a production build of the site, run against a throwaway
// database, in test mode (no Stripe, no Prodigi, emails only logged).
const PORT = 3123;
export default defineConfig({
  testDir: "tests/e2e",
  timeout: 120_000,
  retries: process.env.CI ? 1 : 0,
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: "off",
    launchOptions: { args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"] },
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } }, testIgnore: /mobile\.spec/ },
    { name: "phone", use: { ...devices["Pixel 7"] }, testMatch: /mobile\.spec/ },
  ],
  webServer: {
    command: `rm -rf .e2e-data && npx next start -p ${PORT}`,
    url: `http://127.0.0.1:${PORT}/api/health`,
    reuseExistingServer: false,
    timeout: 120_000,
    env: { DATA_DIR: ".e2e-data", SESSION_SECRET: "e2e-secret-0123456789abcdef0123", ORDER_HOLD_MINUTES: "60", APP_URL: `http://127.0.0.1:${PORT}` },
  },
});
