import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { PUBLIC_SLUGS, pathFor } from "../../src/lib/policy.mjs";

const routes = PUBLIC_SLUGS.map(pathFor);

for (const route of routes) {
  test(`${route} is accessible, indexable and responsive`, async ({
    page,
  }, testInfo) => {
    // The copied branch page includes several external maps, each audited by axe.
    if (route === "/branches/") test.setTimeout(60_000);
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    const response = await page.goto(route, { waitUntil: "domcontentloaded" });
    expect(response?.status()).toBe(200);
    expect(response?.headers()["x-robots-tag"]).toBeUndefined();
    await expect(page.locator("h1")).toHaveCount(1);
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute(
      "href",
      `https://patnampakodi.com${route}`,
    );
    await expect(page.locator('meta[name="description"]')).toHaveAttribute(
      "content",
      /\S.{40}/,
    );
    await expect(page.locator('meta[property="og:title"]')).toHaveAttribute(
      "content",
      /\S/,
    );
    await page.evaluate(() => document.fonts.ready);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
    const accessibility = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa", "best-practice"])
      .analyze();
    expect(accessibility.violations).toEqual([]);
    expect(errors).toEqual([]);
    await page.screenshot({
      path: testInfo.outputPath("page.png"),
      fullPage: true,
    });
    if (route === "/") {
      await page.locator("footer").scrollIntoViewIfNeeded();
      const header = await page.locator(".store-header").boundingBox();
      expect(header!.y).toBe(0);
      const navTrigger =
        testInfo.project.name === "mobile"
          ? page.getByRole("button", { name: "Open menu" })
          : page
              .getByRole("navigation", { name: "Main navigation", exact: true })
              .getByRole("link", { name: "Menu", exact: true });
      await navTrigger.focus();
      await expect(navTrigger).toBeInViewport();
    }
  });
}

test("four-flavour menu and navigation work without JavaScript", async ({
  browser,
}) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3510/menu/?category=Drinks&q=anything");
  await expect(page.locator(".signature-item")).toHaveCount(4);
  await expect(page.getByRole("searchbox")).toHaveCount(0);
  await expect(page.locator("main")).not.toContainText(/\u20b9/);
  for (const name of ["Erra Karam", "Pachi Mirchi", "Miriyala", "Chettinad"])
    await expect(
      page
        .locator(".signature-item")
        .getByRole("heading", { name: new RegExp(name) }),
    ).toBeVisible();
  await context.close();
});

test("branch listings and central contact links remain reachable", async ({
  page,
}) => {
  await page.goto("/branches/");
  await expect(page.locator(".outlet-grid article")).toHaveCount(1);
  await expect(page.locator(".outlet-grid article")).toContainText(
    "Kukatpally",
  );
  await expect(page.getByRole("searchbox")).toHaveCount(0);
  await page
    .locator(".outlet-grid article")
    .first()
    .getByRole("link", { name: "Branch details" })
    .click();
  await expect(
    page.getByRole("link", { name: "Open outlet map" }),
  ).toBeVisible();
  await page.goto("/contact/");
  await expect(page.locator('main a[href="tel:+919000365219"]')).toBeVisible();
  await expect(
    page.locator('main a[href="mailto:patnampakodi@gmail.com"]'),
  ).toBeVisible();
  await expect(page.locator("main")).toContainText("Dr Atmaram Estates");
});

test("sitemap contains only public routes; private and missing routes are noindex", async ({
  request,
}) => {
  const sitemap = await request.get("/sitemap.xml");
  expect(sitemap.ok()).toBe(true);
  const xml = await sitemap.text();
  for (const route of routes)
    expect(xml).toContain(`<loc>https://patnampakodi.com${route}</loc>`);
  expect((xml.match(/<loc>/g) ?? []).length).toBe(7);
  const robots = await request.get("/robots.txt");
  expect(await robots.text()).toContain("Disallow: /checkout/");
  for (const route of [
    "/admin/",
    "/account/",
    "/track/",
    "/missing-page/",
    "/home/",
  ]) {
    const response = await request.get(route);
    expect(response.status()).toBe(
      ["/admin/", "/track/"].includes(route) ? 200 : 404,
    );
    expect(await response.text()).toContain("noindex");
    if (route !== "/missing-page/" && route !== "/home/")
      expect(response.headers()["x-robots-tag"]).toContain("noindex");
  }
});

test("keyboard skip link and mobile navigation work with reduced motion", async ({
  page,
}, testInfo) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(
    page.getByRole("link", { name: "Skip to content" }),
  ).toBeFocused();
  await page.getByRole("link", { name: "Skip to content" }).click();
  await expect(page).toHaveURL(/#main$/);
  if (testInfo.project.name === "mobile") {
    await page.getByRole("button", { name: "Open menu" }).focus();
    await page.keyboard.press("Enter");
    await expect(page.locator(".store-drawer[open] nav")).toBeVisible();
    await page
      .locator(".store-drawer")
      .getByRole("link", { name: "Menu", exact: true })
      .click();
    await expect(page).toHaveURL(/\/menu\/$/);
  }
});
