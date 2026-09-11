import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("original identity and shopping navigation survive responsive layouts", async ({
  page,
}, info) => {
  await page.goto("/");
  await page.evaluate(() => document.fonts.ready);
  await expect(page.locator("html")).toHaveCSS(
    "background-color",
    "rgb(254, 241, 228)",
  );
  await expect(page.locator("body")).toHaveCSS("color", "rgb(53, 53, 53)");
  await expect(page.locator("h1 span")).toHaveCSS("font-weight", "800");
  const typography = await page.evaluate(() => ({
    body: getComputedStyle(document.body).fontFamily,
    heading: getComputedStyle(document.querySelector("h1")!).fontFamily,
  }));
  expect(typography.heading).toBe(typography.body);
  if (info.project.name === "mobile")
    await page
      .locator(".mobile-bottom-nav")
      .getByRole("link", { name: "Shop", exact: true })
      .click();
  else
    await page
      .getByRole("navigation", { name: "Shopping modes" })
      .getByRole("link", { name: "Shop packaged" })
      .click();
  await expect(page).toHaveURL(/\/shop\/$/);
  await page
    .locator(".store-tools")
    .getByRole("link", { name: "Cart, 0 items" })
    .click();
  await expect(page).toHaveURL(/\/cart\/\?mode=packaged$/);
  await expect(
    page.getByRole("heading", { name: "Your cart is empty" }),
  ).toBeVisible();
});

test("original homepage content, local assets and phone-first lead dialog", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Patnam Pakodi.*Made for/, level: 1 }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "What are you craving?" }),
  ).toBeVisible();
  await expect(
    page.locator('header img[src*="656da99ddfd65b8a"]'),
  ).toBeVisible();
  await expect(
    page.getByRole("img", { name: "Kaju Chicken Pakodi", exact: true }),
  ).toHaveAttribute("src", /672607b47463342a/);
  await expect(
    page.getByRole("img", { name: "Kothimeera Chicken Pakodi", exact: true }),
  ).toHaveAttribute("src", /1d5b2efa231d50d8/);
  const trigger = page
    .getByRole("button", { name: "Download brochure", exact: true })
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
  await page.goto("http://127.0.0.1:3510/", { waitUntil: "domcontentloaded" });
  const faq = page.locator(".home-faq details").first();
  await faq.locator("summary").click();
  await expect(faq.locator("p")).toContainText("Display Model");
  await context.close();
});
