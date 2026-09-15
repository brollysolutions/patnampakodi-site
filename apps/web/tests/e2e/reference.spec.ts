import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test("original identity and informational navigation survive responsive layouts", async ({
  page,
}, info) => {
  await page.goto("/");
  await page.evaluate(() => document.fonts.ready);
  await expect(page.locator("html")).toHaveCSS(
    "background-color",
    "rgb(254, 241, 228)",
  );
  await expect(page.locator("body")).toHaveCSS("color", "rgb(53, 53, 53)");
  await expect(page.locator("h1")).toHaveCSS("font-weight", "500");
  const typography = await page.evaluate(() => ({
    body: getComputedStyle(document.body).fontFamily,
    heading: getComputedStyle(document.querySelector("h1")!).fontFamily,
  }));
  expect(typography.heading).toBe(typography.body);
  const mobile = info.project.name === "mobile";
  if (mobile) await page.getByRole("button", { name: "Open menu" }).click();
  const nav = page.getByRole("navigation", {
    name: mobile ? "Mobile navigation" : "Main navigation",
    exact: true,
  });
  await nav.getByRole("link", { name: "Menu", exact: true }).click();
  await expect(page).toHaveURL(/\/menu\/$/);
  await expect(page.locator(".signature-item")).toHaveCount(4);
});

test("original homepage content, local assets and phone-first lead dialog", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", {
      name: /Chicken pakodi.*Full of character/,
      level: 1,
    }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: /A flavour for.*your kind of spice/ }),
  ).toBeVisible();
  await expect(
    page.locator('header img[src*="patnam-logo-refined"]'),
  ).toBeVisible();
  await expect(
    page.getByRole("img", {
      name: "Illustration of Erra Karam Kodi Pakodi",
      exact: true,
    }),
  ).toHaveAttribute("src", /signature-erra-karam/);
  await expect(
    page.getByRole("img", {
      name: "Illustration of Pachi Mirchi Kodi Pakodi",
      exact: true,
    }),
  ).toHaveAttribute("src", /signature-pachi-mirchi/);
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

test("franchise inclusions remain available without JavaScript", async ({
  browser,
}) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto("http://127.0.0.1:3510/franchise/", {
    waitUntil: "domcontentloaded",
  });
  const faq = page.locator(".franchise-inclusions details").first();
  await expect(faq).toHaveAttribute("open", "");
  await expect(faq.locator("p")).toContainText("electric fryer");
  await faq.locator("summary").click();
  await expect(faq).not.toHaveAttribute("open", "");
  await faq.locator("summary").click();
  await expect(faq.locator("p")).toBeVisible();
  await context.close();
});
