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
      await page
        .getByRole("search")
        .getByRole("button", { name: "Search", exact: true })
        .focus();
      await expect(
        page
          .getByRole("search")
          .getByRole("button", { name: "Search", exact: true }),
      ).toBeInViewport();
    }
  });
}

test("menu search, categories, empty results and reset work without JavaScript", async ({
  browser,
}) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3510/menu/", {
    waitUntil: "domcontentloaded",
  });
  await expect(page.locator(".menu-item")).toHaveCount(51);
  await page.getByRole("button", { name: "Drinks", exact: true }).click();
  await expect(page.locator(".menu-item")).toHaveCount(11);
  await page.getByLabel("Find your favourite").fill("Junnu");
  await page
    .locator("main")
    .getByRole("button", { name: "Search", exact: true })
    .click();
  await expect(page.locator(".menu-item")).toHaveCount(1);
  await expect(page).toHaveURL(/category=Drinks/);
  await expect(
    page.getByRole("heading", { name: "Junnu Pot", exact: true }),
  ).toBeVisible();
  await page.getByLabel("Find your favourite").fill("nothingmatches123");
  await page
    .locator("main")
    .getByRole("button", { name: "Search", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "No bites found." }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Show the full menu" }).click();
  await expect(page.locator(".menu-item")).toHaveCount(51);
  await context.close();
});

test("location search resolves a pincode and provides an honest empty state", async ({
  page,
}) => {
  await page.goto("/branches/", { waitUntil: "domcontentloaded" });
  await page.getByLabel("City, neighbourhood or pincode").fill("500081");
  await page.getByRole("button", { name: "Find a store" }).click();
  await expect(page.locator(".outlet-grid article")).toHaveCount(1);
  await expect(
    page.getByRole("heading", { name: "Madhapur", exact: true }),
  ).toBeVisible();
  await page.getByLabel("City, neighbourhood or pincode").fill("000000");
  await page.getByRole("button", { name: "Find a store" }).click();
  await expect(
    page.getByRole("heading", { name: "Let’s try another neighbourhood." }),
  ).toBeVisible();
});

test("contact opens email and shop exposes no draft product or checkout", async ({
  page,
}) => {
  await page.goto("/contact/");
  await expect(
    page.locator('a[href="mailto:patnampakodi@gmail.com"]').first(),
  ).toBeVisible();
  await page.goto("/shop/");
  await expect(page.locator("main")).not.toContainText("unapproved-ready-mix");
  await expect(page.locator('a[href*="checkout"]')).toHaveCount(0);
  await expect(page.locator("main")).toContainText(
    /not available|not open|not yet|preparing/i,
  );
});

test("sitemap contains only public routes; private and missing routes are noindex", async ({
  request,
}) => {
  const sitemap = await request.get("/sitemap.xml");
  expect(sitemap.ok()).toBe(true);
  const xml = await sitemap.text();
  for (const route of routes)
    expect(xml).toContain(`<loc>https://patnampakodi.com${route}</loc>`);
  expect((xml.match(/<loc>/g) ?? []).length).toBe(13);
  const robots = await request.get("/robots.txt");
  expect(await robots.text()).toContain("Disallow: /checkout/");
  for (const route of [
    "/admin/",
    "/account/",
    "/checkout/",
    "/missing-page/",
    "/home/",
  ]) {
    const response = await request.get(route);
    expect(response.status()).toBe(
      ["/admin/", "/checkout/"].includes(route) ? 200 : 404,
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
      .getByRole("link", { name: "Order fresh", exact: true })
      .click();
    await expect(page).toHaveURL(/\/menu\/$/);
  }
});
