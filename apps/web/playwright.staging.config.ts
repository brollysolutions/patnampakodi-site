import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests/staging",
  fullyParallel: false,
  workers: 1,
  retries: 0,
  outputDir: "test-results-staging",
  reporter: [["list"]],
  use: {
    baseURL: process.env.STAGING_FIXTURE_URL,
    viewport: { width: 390, height: 844 },
    isMobile: true,
    hasTouch: true,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
});
