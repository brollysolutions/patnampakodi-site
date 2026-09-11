import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("original homepage content, local assets and phone-first lead dialog", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Patnam Pakodi", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Proprietary Chef-Less SOP Model" }),
  ).toBeVisible();
  await expect(
    page.locator('header img[src*="656da99ddfd65b8a"]'),
  ).toBeVisible();
  const trigger = page
    .getByRole("button", { name: "Become Franchise Partner", exact: true })
    .first();
  await trigger.click();
  const dialog = page.getByRole("dialog", { name: "Franchise enquiry" });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByLabel("Mobile Number")).toBeVisible();
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  let calls = 0;
  await page.route("**/api/v1/enquiries/quick", async (route) => {
    const payload = route.request().postDataJSON();
    expect(payload.phone).toBe("+919876543210");
    expect(payload).not.toHaveProperty("name");
    expect(payload.request_key).toMatch(/^[0-9a-f-]{36}$/);
    calls++;
    await route.fulfill({
      json: {
        detail: "Your enquiry is saved. Our team will contact you.",
        brochure_url: null,
      },
    });
  });
  await dialog.getByLabel("Mobile Number").fill("9876543210");
  await dialog.getByRole("button", { name: "Get Franchise Details" }).click();
  await expect(dialog.getByRole("status")).toContainText(
    "Your enquiry is saved",
  );
  expect(calls).toBe(1);
  await page.keyboard.press("Escape");
  await expect(dialog).not.toBeVisible();
  await expect(trigger).toBeFocused();
});

test("public source FAQ remains available without JavaScript", async ({
  browser,
}) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3010/", { waitUntil: "domcontentloaded" });
  const faq = page.locator("details.reference-faq").first();
  await faq.locator("summary").click();
  await expect(faq.locator("p")).toContainText("Display Model");
  await context.close();
});
