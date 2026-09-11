import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
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
for (const mode of ["fresh", "packaged"] as const) {
  test(`guest ${mode} checkout reviews delivery, preserves baskets and opens immediate payment`, async ({
    page,
  }, info) => {
    test.setTimeout(90_000);
    fixture("checkout");
    try {
      await page.goto("/product/fixture-mix/");
      await page
        .getByRole("button", { name: "Add to cart", exact: true })
        .first()
        .click();
      await page.goto("/product/fixture-fresh/");
      await page
        .getByRole("button", { name: "Add to cart", exact: true })
        .first()
        .click();
      await page
        .getByRole("button", {
          name: "Save Fixture Fresh Pakodi to favourites",
        })
        .click();
      await page.goto("/favourites/");
      await expect(
        page
          .locator("main")
          .getByRole("heading", { name: "Fixture Fresh Pakodi", exact: true }),
      ).toBeVisible();
      await page.goto("/cart/?mode=" + mode);
      await expect(
        page.locator(".basket-row").getByRole("heading"),
      ).toHaveCount(1);
      await expect(page.locator(".basket-modes")).toContainText(
        "Fresh food (1)",
      );
      await expect(page.locator(".basket-modes")).toContainText("Packaged (1)");
      await page.getByRole("link", { name: "Continue to checkout" }).click();
      await page.getByLabel("Full name").fill("Browser Fixture Buyer");
      await page.getByLabel("Phone number", { exact: true }).fill("9876543210");
      await page.getByLabel("Street address").fill("10 Synthetic Test Street");
      await page.getByLabel("City", { exact: true }).fill("Test City");
      await page.getByLabel("PIN code", { exact: true }).fill("999999");
      await page
        .getByRole("combobox", { name: "State", exact: true })
        .selectOption("36");
      await page
        .getByRole("button", { name: "Review order", exact: true })
        .click();
      await expect(
        page
          .locator("main .notice")
          .filter({ hasText: /deliver|available|PIN/i }),
      ).toBeVisible();
      await expect(page.getByLabel("Full name")).toHaveValue(
        "Browser Fixture Buyer",
      );
      await page.getByLabel("PIN code", { exact: true }).fill("500001");
      await page
        .getByRole("button", { name: "Review order", exact: true })
        .click();
      await expect(
        page.getByRole("heading", { name: "Everything look good?" }),
      ).toBeFocused();
      await expect(page.getByLabel("Full name")).not.toBeVisible();
      await expect(page.locator(".checkout-summary")).toContainText("138.00");
      if (mode === "fresh")
        await expect(page.locator("main")).toContainText(
          "Fixture pilot outlet",
        );
      expect(
        (
          await new AxeBuilder({ page })
            .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
            .analyze()
        ).violations,
      ).toEqual([]);
      await page.screenshot({
        path: info.outputPath("checkout-review.png"),
        fullPage: true,
      });
      await page.getByRole("button", { name: /Continue to payment/ }).click();
      await expect(page).toHaveURL(/\/track\/#access=/);
      await expect(
        page.getByRole("button", { name: "Pay securely", exact: true }),
      ).toBeVisible();
      await expect(
        page.getByRole("heading", { name: "Ready for payment", exact: true }),
      ).toBeVisible();
      expect(
        (
          await new AxeBuilder({ page })
            .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
            .analyze()
        ).violations,
      ).toEqual([]);
      await page
        .getByRole("button", { name: "Cancel order", exact: true })
        .click();
      await page
        .getByRole("button", { name: "Confirm cancellation", exact: true })
        .click();
      await expect(
        page.getByRole("heading", { name: "Cancelled", exact: true }),
      ).toBeVisible();
      await page
        .getByRole("button", { name: "Order again", exact: true })
        .click();
      await expect(page).toHaveURL(new RegExp("/cart/\\?mode=" + mode + "$"));
      await expect(page.locator(".basket-modes")).toContainText(
        (mode === "fresh" ? "Fresh food" : "Packaged") + " (2)",
      );
      await expect(page.locator(".basket-modes")).toContainText(
        (mode === "fresh" ? "Packaged" : "Fresh food") + " (1)",
      );
    } finally {
      fixture("reset");
    }
  });
}
