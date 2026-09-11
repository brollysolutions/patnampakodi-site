import { test, expect } from "@playwright/test";
test("public layouts reflow at 320px and a 200-percent desktop viewport", async ({
  page,
}, info) => {
  test.skip(
    info.project.name !== "desktop",
    "One isolated viewport sweep covers all configured routes.",
  );
  test.setTimeout(120_000);
  // 720 CSS px represents a 1440px desktop window at 200% browser zoom.
  for (const width of [320, 720]) {
    await page.setViewportSize({ width, height: 900 });
    for (const route of [
      "/",
      "/menu/",
      "/shop/",
      "/branches/",
      "/about-us/",
      "/franchise/",
      "/contact/",
      "/cart/",
      "/checkout/",
      "/favourites/",
      "/track/",
      "/admin/",
    ]) {
      await page.goto(route, { waitUntil: "domcontentloaded" });
      await page.evaluate(() => document.fonts.ready);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
        route + " at " + width,
      ).toBe(true);
    }
  }
});
