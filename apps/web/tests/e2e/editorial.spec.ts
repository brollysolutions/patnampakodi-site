import { test, expect } from "@playwright/test";
import {
  PUBLIC_SLUGS,
  RETIRED_OUTLETS,
  pathFor,
} from "../../src/lib/policy.mjs";

test("every editorial page has open, independently operable FAQs without JavaScript", async ({
  browser,
}) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  try {
    for (const slug of PUBLIC_SLUGS) {
      await page.goto(`http://127.0.0.1:3510${pathFor(slug)}`);
      const faqs = page.locator(".editorial-faq details");
      expect(await faqs.count(), slug).toBeGreaterThanOrEqual(3);
      expect(
        await faqs.evaluateAll((items) =>
          items.every((item) => item.hasAttribute("open")),
        ),
        slug,
      ).toBe(true);
      const first = faqs.first();
      await expect(first.locator("p")).toBeVisible();
      await first.locator("summary").click();
      await expect(first.locator("p")).not.toBeVisible();
      await expect(faqs.nth(1).locator("p")).toBeVisible();
      await first.locator("summary").click();
      await expect(first.locator("p")).toBeVisible();
    }
  } finally {
    await context.close();
  }
});

test("Kukatpally is the only current outlet and older URLs show a truthful noindex notice", async ({
  page,
  request,
}) => {
  const content = await (await request.get("/api/v1/storefront")).json();
  expect(content.outlets.map((item: { slug: string }) => item.slug)).toEqual([
    "kukatpally",
  ]);
  const sitemap = await (await request.get("/sitemap.xml")).text();
  expect(sitemap).toContain("/branches/kukatpally/");
  for (const [slug, name] of Object.entries(RETIRED_OUTLETS)) {
    expect(sitemap).not.toContain(`/branches/${slug}/`);
    await page.goto(`/branches/${slug}/`);
    await expect(page.locator("h1")).toContainText(`${name} branch update`);
    await expect(page.locator("main")).toContainText("currently serving only");
    await expect(page.locator('meta[name="robots"]')).toHaveAttribute(
      "content",
      /noindex/,
    );
    await expect(
      page.locator('main a[href="/branches/kukatpally/"]'),
    ).toBeVisible();
    await expect(page.locator('main a[href^="tel:"]')).toHaveCount(0);
  }
});
