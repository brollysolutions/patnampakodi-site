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
  return execFileSync(python, ["tests/browser_fixture.py", mode], {
    cwd: resolve("../api"),
    env: { ...process.env, APP_ENV: "test" },
    encoding: "utf8",
    windowsHide: true,
  });
}

test("customer request, staff approval, private access and cancellation", async ({
  page,
  browser,
}, info) => {
  // This journey provisions fixtures and audits four screens in separate sessions.
  test.setTimeout(60_000);
  const data = JSON.parse(fixture("prepare"));
  try {
    await page.goto("/shop/fixture-mix/");
    await expect(
      page.getByRole("heading", { name: "Fixture Mix", exact: true }),
    ).toBeVisible();
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute(
      "href",
      "https://patnampakodi.com/shop/fixture-mix/",
    );
    expect(
      (
        await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
      ).violations,
    ).toEqual([]);
    await page
      .getByRole("button", { name: "Add to cart", exact: true })
      .click();
    await page.getByRole("link", { name: "View cart", exact: true }).click();
    await page.getByLabel("Full name").fill("Browser Fixture Buyer");
    await page.getByLabel("Phone including +91").fill("+919876543210");
    await page.getByLabel("Street address").fill("10 Synthetic Test Street");
    await page.getByLabel("City", { exact: true }).fill("Test City");
    await page
      .getByRole("combobox", { name: "State", exact: true })
      .selectOption("36");
    await page.getByLabel("Pincode", { exact: true }).fill("500001");
    expect(
      (
        await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
      ).violations,
    ).toEqual([]);
    await page
      .getByRole("button", { name: "Request delivery", exact: true })
      .click();
    await expect(page).toHaveURL(/\/track\/#access=/);
    await expect(
      page.getByRole("button", { name: "Refresh status" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Pay securely" }),
    ).toHaveCount(0);
    const privateURL = page.url();
    const token = new URLSearchParams(new URL(privateURL).hash.slice(1)).get(
      "access",
    )!;
    const order = await (
      await page.request.get("/api/v1/order", {
        headers: { Authorization: "Bearer " + token },
      })
    ).json();
    const staffContext = await browser.newContext();
    const admin = await staffContext.newPage();
    await admin.goto("http://127.0.0.1:3010/admin/");
    await admin.getByLabel("Username", { exact: true }).fill("browser-admin");
    await admin
      .getByLabel("Password", { exact: true })
      .fill("a-strong-browser-fixture-password");
    await admin
      .getByLabel("Authenticator or recovery code")
      .fill(data.recovery);
    await admin.getByRole("button", { name: "Sign in", exact: true }).click();
    await expect(
      admin.getByRole("heading", { name: order.reference }),
    ).toBeVisible();
    expect(
      (
        await new AxeBuilder({ page: admin })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
      ).violations,
    ).toEqual([]);
    await admin.getByLabel(/Delivery fee/).fill("20");
    await admin
      .getByRole("button", { name: "Confirm delivery & quote" })
      .click();
    await expect(
      admin.getByText("Ready for payment", { exact: true }),
    ).toBeVisible();
    await page.getByRole("button", { name: "Refresh status" }).click();
    await expect(
      page.getByRole("button", { name: "Pay securely" }),
    ).toBeVisible();
    await expect(page.locator('meta[name="robots"]')).toHaveAttribute(
      "content",
      /noindex/,
    );
    expect(
      (
        await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
      ).violations,
    ).toEqual([]);
    await page.screenshot({
      path: info.outputPath("private-order.png"),
      fullPage: true,
    });
    const stranger = await browser.newContext();
    const anonymous = await stranger.newPage();
    await anonymous.goto("http://127.0.0.1:3010/track/");
    await expect(anonymous.locator("main")).not.toContainText(
      "Browser Fixture Buyer",
    );
    expect(
      (
        await anonymous.request.get("http://127.0.0.1:3010/api/v1/admin/orders")
      ).status(),
    ).toBe(401);
    await page
      .getByRole("button", { name: "Cancel order", exact: true })
      .click();
    await page.getByRole("button", { name: "Confirm cancellation" }).click();
    await expect(
      page.getByRole("heading", { name: "Cancelled", exact: true }),
    ).toBeVisible();
    await stranger.close();
    await staffContext.close();
  } finally {
    fixture("reset");
  }
});
