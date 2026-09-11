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
    // Legacy staff quotes remain manageable through existing private order links.
    const submitted = await page.request.post("/api/v1/orders", {
      headers: { Origin: "http://127.0.0.1:3510" },
      data: {
        request_key: crypto.randomUUID(),
        customer: {
          name: "Browser Fixture Buyer",
          phone: "+919876543210",
          address: "10 Synthetic Test Street",
          city: "Test City",
          state_code: "36",
          pincode: "500001",
        },
        lines: [{ variant_id: data.variant, quantity: 1 }],
        whatsapp_consent: false,
      },
    });
    expect(submitted.status()).toBe(201);
    const receipt = await submitted.json();
    await page.goto("/track/#access=" + receipt.access_token);

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
    await admin.goto("http://127.0.0.1:3510/admin/");
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
    await anonymous.goto("http://127.0.0.1:3510/track/");
    await expect(anonymous.locator("main")).not.toContainText(
      "Browser Fixture Buyer",
    );
    expect(
      (
        await anonymous.request.get("http://127.0.0.1:3510/api/v1/admin/orders")
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
