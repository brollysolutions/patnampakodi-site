import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";

function fixture(mode: string) {
  const python = resolve(
    "../api",
    process.platform === "win32"
      ? ".venv/Scripts/python.exe"
      : ".venv/bin/python",
  );
  execFileSync(python, ["tests/browser_fixture.py", mode], {
    cwd: resolve("../api"),
    env: { ...process.env, APP_ENV: "test" },
    windowsHide: true,
  });
}
test("catalog discovery, original URLs and quantity cart work together", async ({
  page,
  request,
  browser,
}, info) => {
  test.setTimeout(90_000);
  fixture("prepare");
  try {
    const redirect = await request.get("/shop/fixture-mix/", {
      maxRedirects: 0,
    });
    expect(redirect.status()).toBe(308);
    expect(redirect.headers().location).toBe("/product/fixture-mix/");
    expect((await request.get("/product/missing-product/")).status()).toBe(404);
    expect((await request.get("/product-tag/missing-tag/")).status()).toBe(404);
    const sitemap = await (await request.get("/sitemap.xml")).text();
    expect(sitemap).toContain("/product/fixture-mix/");
    expect(sitemap).toContain("/product-category/fixture-mixes/");
    expect(sitemap).toContain("/product-tag/fixture-pepper/");
    expect(sitemap).not.toContain("/shop/fixture-mix/");
    await page.goto("/shop/", { waitUntil: "domcontentloaded" });
    await page.getByLabel("Search products").fill("does not match");
    await page.getByRole("button", { name: "Apply filters" }).click();
    await expect(
      page.getByRole("heading", { name: "No products match these filters" }),
    ).toBeVisible();
    await page.goto(
      "/product-category/fixture-mixes/?tag=fixture-pepper&sort=price-asc",
      { waitUntil: "domcontentloaded" },
    );
    await expect(
      page.getByRole("heading", { name: "Fixture Mix", exact: true }),
    ).toBeVisible();
    await page
      .getByRole("link", { name: "Fixture Mix", exact: true })
      .last()
      .click();
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute(
      "href",
      "https://patnampakodi.com/product/fixture-mix/",
    );
    await expect(page.locator("main del")).toContainText("150.00");
    expect(
      (
        await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
      ).violations,
    ).toEqual([]);
    await page.getByLabel("Quantity", { exact: true }).fill("0");
    await page
      .getByRole("button", { name: "Add to cart", exact: true })
      .click();
    await expect(page.getByRole("status")).toContainText(
      "Choose a quantity from 1 to 100",
    );
    await page.getByLabel("Quantity", { exact: true }).fill("2");
    await page
      .getByRole("button", { name: "Add to cart", exact: true })
      .click();
    await expect(page.getByRole("status")).toContainText("Added to your cart");
    await page.screenshot({
      path: info.outputPath("product.png"),
      fullPage: true,
    });
    await page.getByRole("link", { name: "View cart", exact: true }).click();
    await expect(page.locator("main")).toContainText("236.00");
    const plain = await browser.newContext({ javaScriptEnabled: false });
    try {
      const withoutJS = await plain.newPage();
      await withoutJS.goto(
        "http://127.0.0.1:3010/product-tag/fixture-pepper/?q=Fixture&category=fixture-mixes",
        { waitUntil: "domcontentloaded" },
      );
      await expect(
        withoutJS.getByRole("heading", { name: "Fixture Mix", exact: true }),
      ).toBeVisible();
    } finally {
      await plain.close();
    }
  } finally {
    fixture("reset");
  }
});
