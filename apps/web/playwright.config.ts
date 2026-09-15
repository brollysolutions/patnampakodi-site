import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  ...(process.env.PAKODI_BROWSER_PROFILE === "commerce"
    ? { testMatch: /(?:commerce|checkout|catalog|admin)\.spec\.ts$/ }
    : { testIgnore: /(?:commerce|checkout|catalog|admin)\.spec\.ts$/ }),
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [
    ["list"],
    [
      "html",
      {
        open: "never",
        outputFolder: `playwright-report/${process.env.PAKODI_BROWSER_PROFILE ?? "menu"}`,
      },
    ],
  ],
  outputDir: `test-results/${process.env.PAKODI_BROWSER_PROFILE ?? "menu"}`,
  use: {
    baseURL: "http://127.0.0.1:3510",
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 1000 } } },
    {
      name: "mobile",
      use: {
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
      },
    },
    { name: "tablet", use: { viewport: { width: 768, height: 1024 } } },
  ],
});
