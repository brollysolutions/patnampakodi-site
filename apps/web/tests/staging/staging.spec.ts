import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { execFileSync } from "node:child_process";

function compose(...args: string[]) {
  const project = process.env.STAGING_FIXTURE_PROJECT ?? "";
  if (!/^pakodi_stage_fixture_[a-f0-9]{12}$/.test(project))
    throw Error("Disposable fixture project required");
  const file = process.env.STAGING_FIXTURE_COMPOSE!;
  return execFileSync(
    "docker",
    ["compose", "-f", file, "-p", project, ...args],
    {
      env: {
        ...process.env,
        COMPOSE_DISABLE_ENV_FILE: "1",
        COMPOSE_ENV_FILES: "",
      },
      windowsHide: true,
      encoding: "utf8",
    },
  );
}

test("Docker checkout, signed replay, worker recovery, delivery and partial refund", async ({
  page,
  browser,
}, info) => {
  test.setTimeout(180_000);
  const origin = process.env.STAGING_FIXTURE_URL!;
  if (!/^http:\/\/127\.0\.0\.1:\d+$/.test(origin))
    throw Error("Loopback fixture URL required");
  const data = JSON.parse(process.env.STAGING_FIXTURE_DATA!);
  const externalPayments: string[] = [];
  page.on("request", (request) => {
    if (/razorpay\.com|graph\.facebook\.com/.test(request.url()))
      externalPayments.push(request.url());
  });
  const productResponse = await page.goto("/product/staging-fixture-mix/");
  expect(productResponse?.headers()["x-robots-tag"]).toContain("noindex");
  await expect(page.locator('meta[name="robots"]')).toHaveAttribute(
    "content",
    /noindex/,
  );
  await page.getByRole("button", { name: "Add to cart", exact: true }).click();
  await page.getByRole("link", { name: "View cart", exact: true }).click();
  await page.getByRole("link", { name: "Continue to checkout" }).click();
  await page.getByLabel("Full name").fill("Synthetic Staging Buyer");
  await page.getByLabel("Phone number", { exact: true }).fill("+919876543210");
  await page.getByLabel("Street address").fill("10 Synthetic Fixture Street");
  await page.getByLabel("City", { exact: true }).fill("Fixture City");
  await page
    .getByRole("combobox", { name: "State", exact: true })
    .selectOption("36");
  await page.getByLabel("PIN code", { exact: true }).fill("500001");
  await page.getByLabel(/WhatsApp/).check();
  await page.getByRole("button", { name: "Review order", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Everything look good?" }),
  ).toBeVisible();
  await page.getByRole("button", { name: /Continue to payment/ }).click();
  await expect(page).toHaveURL(/\/track\/#access=/);
  const token = new URLSearchParams(new URL(page.url()).hash.slice(1)).get(
    "access",
  )!;
  const auth = { Authorization: "Bearer " + token };
  const order = await (
    await page.request.get("/api/v1/order", { headers: auth })
  ).json();
  const context = await browser.newContext({
    baseURL: origin,
    viewport: page.viewportSize() ?? { width: 390, height: 844 },
  });
  const admin = await context.newPage();
  await admin.goto("/admin/");
  await admin
    .getByLabel("Username", { exact: true })
    .fill("staging-fixture-admin");
  await admin
    .getByLabel("Password", { exact: true })
    .fill("synthetic-staging-only-password");
  await admin.getByLabel("Authenticator or recovery code").fill(data.recovery);
  await admin.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    admin.getByRole("heading", { name: order.reference }),
  ).toBeVisible();
  await expect(
    admin.getByRole("button", { name: "Confirm delivery & quote" }),
  ).toHaveCount(0);
  await expect(
    admin.getByText("Ready for payment", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Refresh status" }).click();
  await page.getByRole("button", { name: "Pay securely" }).click();
  await expect(
    page.getByRole("button", { name: "Confirm test payment" }),
  ).toBeVisible({ timeout: 30000 });
  compose("stop", "worker");
  await page.getByRole("button", { name: "Confirm test payment" }).click();
  await expect(page.getByText(/Local test payment submitted/)).toBeVisible();
  const pending = await (
    await page.request.get("/api/v1/order", { headers: auth })
  ).json();
  expect(pending.status).toBe("payment_pending");
  compose("restart", "fixture-provider");
  compose("up", "-d", "--wait", "fixture-provider");
  // The provider persisted before delivery; replay after restart keeps one capture/event.
  const replay = await page.request.post("/api/v1/order/fixture-capture", {
    headers: { ...auth, Origin: origin },
    data: { quote_version: pending.quote_version },
  });
  expect(replay.status()).toBe(200);
  compose("up", "-d", "--wait", "worker");
  await expect
    .poll(
      async () =>
        (
          await (
            await page.request.get("/api/v1/order", { headers: auth })
          ).json()
        ).status,
      { timeout: 30000 },
    )
    .toBe("paid");
  await page.getByRole("button", { name: "Refresh status" }).click();
  await expect(
    page.getByRole("button", { name: "Download invoice" }),
  ).toBeVisible();
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          JSON.parse(localStorage.getItem("pakodi-shopping-v2")!).carts.packaged
            .length,
      ),
    )
    .toBe(0);
  const invoice = await page.request.get("/api/v1/order/invoice", {
    headers: auth,
  });
  expect(invoice.status()).toBe(200);
  expect((await invoice.body()).subarray(0, 4).toString()).toBe("%PDF");
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await page.screenshot({
    path: info.outputPath("docker-paid-order.png"),
    fullPage: true,
  });
  await admin.reload();
  await admin.getByRole("button", { name: "Mark dispatched" }).click();
  await admin.getByRole("button", { name: "Mark delivered" }).click();
  await expect(admin.getByText("Delivered", { exact: true })).toBeVisible();
  await admin
    .getByText("Cancellation, refund, and link recovery", { exact: true })
    .click();
  await admin.getByLabel("Refund amount in INR").fill("20");
  await admin
    .getByLabel("Refund reason", { exact: true })
    .fill("Synthetic acceptance refund");
  await admin
    .getByRole("button", { name: "Request refund", exact: true })
    .click();
  await expect
    .poll(
      async () => {
        const start = new Date(Date.now() - 86400000)
          .toISOString()
          .slice(0, 10);
        const end = new Date(Date.now() + 86400000).toISOString().slice(0, 10);
        const result = await (
          await admin.request.get(
            `/api/v1/admin/sales-summary?start=${start}&end=${end}`,
          )
        ).json();
        return {
          orders: result.orders,
          gross: result.gross_paise,
          refunded: result.refunded_paise,
          net: result.net_paise,
        };
      },
      { timeout: 30000 },
    )
    .toEqual({ orders: 1, gross: 13800, refunded: 2000, net: 11800 });
  await expect
    .poll(
      async () =>
        (await (await admin.request.get("/api/v1/admin/messages")).json()).some(
          (item: { status: string }) => item.status === "delivered",
        ),
      { timeout: 30000 },
    )
    .toBe(true);
  await admin
    .getByRole("navigation", { name: "Administration" })
    .getByRole("button", { name: "Reports", exact: true })
    .click();
  await admin
    .getByLabel("Sales from date")
    .fill(new Date(Date.now() - 86400000).toISOString().slice(0, 10));
  await admin
    .getByLabel("Sales to date")
    .fill(new Date(Date.now() + 86400000).toISOString().slice(0, 10));
  await admin.getByRole("button", { name: "Load sales summary" }).click();
  const report = admin.getByRole("region", {
    name: "Daily sales",
    exact: true,
  });
  await expect(report.getByRole("row")).toHaveCount(2);
  await report.focus();
  await expect(report).toBeFocused();
  expect(
    (
      await new AxeBuilder({ page: admin })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await admin.screenshot({
    path: info.outputPath("docker-sales-report.png"),
    fullPage: true,
  });

  await admin
    .getByRole("navigation", { name: "Administration" })
    .getByRole("button", { name: "Delivery", exact: true })
    .click();
  await expect(
    admin.getByRole("heading", { name: "Delivery & fresh food" }),
  ).toBeVisible();
  await admin.getByLabel("Pause new fresh orders").check();
  await admin
    .getByRole("button", { name: "Save delivery settings", exact: true })
    .click();
  await expect(
    admin.getByRole("status").filter({ hasText: "Delivery settings saved" }),
  ).toBeVisible();
  expect(
    (
      await (
        await page.request.get(
          "/api/v1/serviceability?mode=fresh&pincode=500001",
        )
      ).json()
    ).available,
  ).toBe(false);
  await admin.getByLabel("Pause new fresh orders").uncheck();
  await admin
    .getByRole("button", { name: "Save delivery settings", exact: true })
    .click();
  await expect(
    admin.getByRole("status").filter({ hasText: "Delivery settings saved" }),
  ).toBeVisible();
  expect(
    (
      await (
        await page.request.get(
          "/api/v1/serviceability?mode=fresh&pincode=500001",
        )
      ).json()
    ).available,
  ).toBe(true);
  expect(
    (
      await new AxeBuilder({ page: admin })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await admin.screenshot({
    path: info.outputPath("docker-delivery-settings.png"),
    fullPage: true,
  });

  const variant = (
    await (await admin.request.get("/api/v1/admin/variants")).json()
  ).find((item: { id: string }) => item.id === data.variant);
  const csrf = (await context.cookies()).find(
    (cookie) => cookie.name === "pakodi_csrf",
  )!.value;
  const productInput = {
    sku: variant.sku,
    product: variant.product,
    gst_bps: variant.gst_bps,
    hsn: variant.hsn,
    published: variant.published,
    media_id: variant.media_id,
  };
  const productHeaders = { Origin: origin, "X-CSRF-Token": csrf };
  try {
    expect(
      (
        await admin.request.put(`/api/v1/admin/variants/${data.variant}`, {
          headers: productHeaders,
          data: {
            ...productInput,
            product: { ...variant.product, image: "" },
            media_id: null,
          },
        })
      ).status(),
    ).toBe(200);
    await page.goto("/product/staging-fixture-mix/");
    await expect(
      page.locator(".product-detail-image .product-image-placeholder"),
    ).toBeVisible();
    await expect(
      page.getByRole("button", {
        name: "Save Staging Fixture Mix to favourites",
      }),
    ).toBeVisible();
    await page.screenshot({
      path: info.outputPath("docker-product-without-photo.png"),
      fullPage: true,
    });
  } finally {
    expect(
      (
        await admin.request.put(`/api/v1/admin/variants/${data.variant}`, {
          headers: productHeaders,
          data: productInput,
        })
      ).status(),
    ).toBe(200);
  }
  expect(externalPayments).toEqual([]);
  await context.close();
});

test("a public content outage shows a recoverable error without stale content", async ({
  page,
}, info) => {
  test.setTimeout(90_000);
  await page.goto("/contact/");
  const heading = await page.locator("main h1").innerText();
  const title = await page.title();
  try {
    compose("stop", "api");
    const failed = await page.reload();
    expect(failed?.status()).toBe(500);
    await expect(
      page.getByRole("heading", { name: "We couldn’t load this page" }),
    ).toBeVisible();
    await expect(page).toHaveTitle("Page unavailable | Patnam Pakodi");
    await expect(page.locator("main h1")).not.toHaveText(heading);
    expect(
      (
        await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
      ).violations,
    ).toEqual([]);
    await page.screenshot({
      path: info.outputPath("docker-content-unavailable.png"),
      fullPage: true,
    });
  } finally {
    compose("up", "-d", "--wait", "api");
  }
  await page.getByRole("button", { name: "Try again", exact: true }).click();
  await expect(page.locator("main h1")).toHaveText(heading);
  await expect(page).toHaveTitle(title);
});
