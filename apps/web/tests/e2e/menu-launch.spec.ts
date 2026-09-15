import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import { PUBLIC_SLUGS, pathFor } from "../../src/lib/policy.mjs";

function fixture(mode: string) {
  return execFileSync(
    resolve(
      "../api",
      process.platform === "win32"
        ? ".venv/Scripts/python.exe"
        : ".venv/bin/python",
    ),
    ["tests/browser_fixture.py", mode],
    {
      cwd: resolve("../api"),
      env: { ...process.env, APP_ENV: "test" },
      encoding: "utf8",
      windowsHide: true,
    },
  );
}

test("public pages expose only informational navigation and no shopping controls", async ({
  page,
  request,
}) => {
  expect(
    (await (await request.get("/api/v1/storefront")).json()).ordering_enabled,
  ).toBe(false);
  for (const path of PUBLIC_SLUGS.map(pathFor)) {
    await page.goto(path);
    await expect(page.getByRole("searchbox")).toHaveCount(0);
    await expect(
      page.locator(
        'a[href^="/shop/"], a[href^="/cart/"], a[href^="/favourites/"], a[href^="/checkout/"], a[href^="/track/"]',
      ),
    ).toHaveCount(0);
    await expect(
      page.getByRole("button", {
        name: /add to cart|check your pin|save .*favourites/i,
      }),
    ).toHaveCount(0);
  }
});

test("paused shopping URLs redirect even with published stock and stale browser storage", async ({
  page,
  request,
}) => {
  fixture("checkout");
  try {
    const catalogue = await (await request.get("/api/v1/catalog")).json();
    expect(catalogue).toHaveLength(2);
    for (const path of [
      "/shop/",
      "/product/fixture-mix/",
      "/shop/fixture-mix/",
      "/product-category/fixture-mixes/",
      "/product-tag/fixture-pepper/",
      "/cart/?mode=fresh",
      "/checkout/",
      "/favourites/",
    ]) {
      const response = await request.get(path, { maxRedirects: 0 });
      expect(response.status(), path).toBe(307);
      expect(response.headers().location).toBe("/menu/");
    }
    const fresh = catalogue.find(
      (item: { product: { mode: string } }) => item.product.mode === "fresh",
    );
    await page.addInitScript(
      (id) =>
        localStorage.setItem(
          "pakodi-shopping-v2",
          JSON.stringify({
            mode: "fresh",
            favourites: [id],
            carts: {
              fresh: [{ variant_id: id, quantity: 2 }],
              packaged: [],
            },
          }),
        ),
      fresh.id,
    );
    await page.goto("/checkout/?mode=fresh");
    await expect(page).toHaveURL(/\/menu\/$/);
    await expect(page.locator(".signature-item")).toHaveCount(4);
    await expect(page.locator("main")).not.toContainText("Fixture Mix");
    const sitemap = await (await request.get("/sitemap.xml")).text();
    expect(sitemap).not.toMatch(
      /\/product\/|\/product-category\/|\/product-tag\/|\/shop\//,
    );
  } finally {
    fixture("reset");
  }
});

test("existing private order links retain status and cancellation without payment or reorder", async ({
  page,
}) => {
  const { token } = JSON.parse(fixture("history"));
  try {
    await page.goto("/track/#access=" + token);
    await expect(
      page.getByRole("button", { name: "Refresh status" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: /pay securely|reorder|order again/i }),
    ).toHaveCount(0);
    await expect(page.locator('script[src*="razorpay"]')).toHaveCount(0);
    await expect(
      page.getByRole("button", { name: "Cancel order", exact: true }),
    ).toBeVisible();
    const response = await page.request.post("/api/v1/order/payment", {
      headers: {
        Authorization: "Bearer " + token,
        Origin: "http://127.0.0.1:3510",
      },
      data: { quote_version: 1 },
    });
    expect(response.status()).toBe(409);
  } finally {
    fixture("reset");
  }
});

test("brochure packages, contact details and the optimized PDF are available", async ({
  page,
  request,
}) => {
  await page.goto("/franchise/");
  await expect(page.locator(".signature-models article")).toHaveCount(4);
  for (const price of ["69,000", "99,000", "1,50,000", "3,00,000"])
    await expect(
      page.locator(".franchise-price").filter({ hasText: price }),
    ).toBeVisible();
  const response = await request.get("/api/v1/brochure");
  expect(response.ok()).toBe(true);
  expect(response.headers()["content-type"]).toContain("application/pdf");
  const pdf = await response.body();
  expect(pdf.byteLength).toBeLessThan(5_000_000);
  expect(pdf.subarray(0, 5).toString()).toBe("%PDF-");
});
