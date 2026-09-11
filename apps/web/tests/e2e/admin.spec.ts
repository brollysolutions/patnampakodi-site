import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { execFileSync } from "node:child_process";
import { resolve } from "node:path";
import { randomUUID } from "node:crypto";

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

test("staff enriches a lead, exports CSV, reports sales and selects draft media", async ({
  page,
}, info) => {
  test.setTimeout(90_000);
  const data = JSON.parse(fixture("prepare"));
  try {
    const lead = await page.request.post("/api/v1/enquiries/quick", {
      headers: { Origin: "http://127.0.0.1:3510" },
      data: {
        request_key: randomUUID(),
        phone: "+919876543210",
        purpose: "brochure",
        source: "browser-fixture",
      },
    });
    expect(lead.status()).toBe(201);
    await page.goto("/admin/");
    await page.getByLabel("Username", { exact: true }).fill("browser-admin");
    await page
      .getByLabel("Password", { exact: true })
      .fill("a-strong-browser-fixture-password");
    await page.getByRole("button", { name: "Sign in", exact: true }).click();
    const navigation = page.getByRole("navigation", { name: "Administration" });
    await navigation
      .getByRole("button", { name: "Products", exact: true })
      .click();
    await page.getByLabel("Find a food or flavour").fill("Chettinadu");
    await page
      .getByRole("button", {
        name: "Prepare Chettinadu Pakodi Ready Mix",
        exact: true,
      })
      .click();
    await expect(
      page.getByRole("heading", {
        name: "Set up Chettinadu Pakodi Ready Mix",
        exact: true,
      }),
    ).toBeFocused();
    await expect(page.getByLabel("Product name", { exact: true })).toHaveValue(
      "Chettinadu Pakodi Ready Mix",
    );
    await expect(page.getByLabel("Permanent product URL slug")).toHaveValue(
      "chettinadu-pakodi-ready-mix",
    );
    await expect(page.getByLabel("Price in INR including tax")).toHaveValue("");
    await expect(page.getByLabel("Allergens", { exact: true })).toHaveValue("");
    await expect(
      page.getByRole("combobox", { name: "Dietary mark", exact: true }),
    ).toHaveValue("");
    await page
      .getByRole("button", { name: "Add another product", exact: true })
      .click();
    await expect(page.getByLabel("Product name", { exact: true })).toHaveValue(
      "",
    );
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page
      .getByRole("button", { name: "Save product", exact: true })
      .scrollIntoViewIfNeeded();
    // Long forms must leave store navigation reachable at every supported width.
    const topbar = await page.locator(".admin-topbar").boundingBox();
    const navBounds = await navigation.boundingBox();
    expect(topbar!.y).toBe(0);
    expect(navBounds!.y).toBeGreaterThanOrEqual(topbar!.height);
    expect(navBounds!.y + navBounds!.height).toBeLessThanOrEqual(
      page.viewportSize()!.height,
    );
    await navigation
      .getByRole("button", { name: "Enquiries", exact: true })
      .click();
    await expect(
      page.getByRole("heading", { name: "Enquiries", exact: true }),
    ).toBeFocused();
    await page.getByText("Edit enquiry details", { exact: true }).click();
    await page
      .getByLabel("Contact name", { exact: true })
      .fill("Browser Lead Fixture");
    await page.getByLabel("Contact city", { exact: true }).fill("Fixture City");
    await page.getByLabel("Staff notes", { exact: true }).fill("=SUM(1,2)");
    await page
      .getByRole("button", { name: "Save enquiry details", exact: true })
      .click();
    await expect(
      page.getByRole("heading", { name: "Browser Lead Fixture" }),
    ).toBeVisible();
    await expect(
      page.getByText("Interest: Brochure", { exact: true }),
    ).toBeVisible();
    await page
      .getByRole("combobox", { name: "Pipeline status", exact: true })
      .selectOption("qualified");
    await page
      .getByRole("button", { name: "Update status", exact: true })
      .click();
    await expect(
      page.getByRole("combobox", { name: "Pipeline status", exact: true }),
    ).toHaveValue("qualified");
    // A short inclusive range around today avoids a midnight timezone race.
    const start = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    const end = new Date(Date.now() + 86400000).toISOString().slice(0, 10);
    await page.getByLabel("Enquiries from date").fill(start);
    await page.getByLabel("Enquiries to date").fill(end);
    await page
      .getByRole("combobox", { name: "Enquiry export status", exact: true })
      .selectOption("qualified");
    const downloaded = page.waitForEvent("download");
    await page.getByRole("button", { name: "Download enquiries CSV" }).click();
    const download = await downloaded;
    expect(download.suggestedFilename()).toBe("enquiries.csv");
    const stream = await download.createReadStream();
    const chunks: Buffer[] = [];
    for await (const chunk of stream!) chunks.push(Buffer.from(chunk));
    const csv = Buffer.concat(chunks).toString("utf8");
    expect(csv).toContain("'Browser Lead Fixture");
    expect(csv).toContain("'=SUM(1,2)");
    expect(csv).toContain("brochure");
    expect(
      (
        await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
      ).violations,
    ).toEqual([]);
    await page.screenshot({
      path: info.outputPath("admin-enquiries.png"),
      fullPage: true,
    });

    await navigation
      .getByRole("button", { name: "Reports", exact: true })
      .click();
    await page.getByLabel("Sales from date").fill(start);
    await page.getByLabel("Sales to date").fill(end);
    await page.getByRole("button", { name: "Load sales summary" }).click();
    await expect(
      page.getByText("No invoiced sales in this period."),
    ).toBeVisible();
    expect(
      (
        await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
      ).violations,
    ).toEqual([]);

    await navigation
      .getByRole("button", { name: "Media", exact: true })
      .click();
    await page
      .getByLabel("JPEG, PNG, or WebP (up to 5 MB)")
      .setInputFiles(
        resolve("public/images/live/pepper-pakodi-ready-mix.webp"),
      );
    await page
      .getByLabel("Image description", { exact: true })
      .fill("Browser draft image");
    await page
      .getByRole("button", { name: "Upload image", exact: true })
      .click();
    const preview = page.getByRole("img", {
      name: "Browser draft image",
      exact: true,
    });
    await expect(preview).toBeVisible();
    const imageURL = (await preview.getAttribute("src"))!;
    expect((await page.request.get(imageURL)).status()).toBe(200);
    expect(
      (
        await page.request.get(imageURL.replace("/admin/media/", "/media/"))
      ).status(),
    ).toBe(404);
    await navigation
      .getByRole("button", { name: "Products", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Edit product", exact: true })
      .click();
    await page
      .getByRole("combobox", { name: "Product image", exact: true })
      .selectOption({ label: "Browser draft image" });
    await expect(
      page.getByRole("img", { name: "Browser draft image", exact: true }),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "Save product", exact: true })
      .click();
    await expect(page.getByText("Saved.", { exact: true })).toBeVisible();
    const products = await (
      await page.request.get("/api/v1/admin/variants")
    ).json();
    expect(products[0].media_id).toBe(imageURL.split("/").pop());
    expect(products[0].product.tags).toEqual(["fixture-pepper"]);
    expect(
      (
        await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
      ).violations,
    ).toEqual([]);
    await page.screenshot({
      path: info.outputPath("admin-products.png"),
      fullPage: true,
    });
  } finally {
    fixture("reset");
  }
});
