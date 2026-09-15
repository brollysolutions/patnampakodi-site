import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  SIGNATURE_SLUGS,
  PUBLIC_SLUGS,
  NAVIGATION,
} from "../../src/lib/policy.mjs";
const records = JSON.parse(
  readFileSync(
    new URL("../../../api/content/storefront.json", import.meta.url),
    "utf8",
  ),
);

test("the published menu contains exactly the approved four flavours without food prices", () => {
  const menu = records
    .filter((row) => row.kind === "menu" && row.published)
    .sort((a, b) => a.position - b.position);
  assert.deepEqual(
    menu.map((row) => row.slug),
    SIGNATURE_SLUGS,
  );
  assert.deepEqual(
    menu.map((row) => row.payload.name),
    [
      "Erra Karam Kodi Pakodi",
      "Pachi Mirchi Kodi Pakodi",
      "Miriyala Kodi Pakodi",
      "Chettinad Kodi Pakodi",
    ],
  );
  for (const row of menu) {
    assert.equal(row.payload.price_paise, null);
    assert.equal(row.payload.dietary, "non-veg");
    assert.match(
      row.payload.image,
      /^\/images\/live\/signature-[a-z-]+\.webp$/,
    );
    assert.ok(
      readFileSync(new URL("../../public" + row.payload.image, import.meta.url))
        .length,
    );
  }
});
test("navigation and route manifest expose only the approved informational destinations", () => {
  assert.deepEqual(
    NAVIGATION.map(([label]) => label),
    ["Menu", "Our Story", "Franchise", "Branches", "Contact"],
  );
  assert.deepEqual(
    new Set(NAVIGATION.map(([, path]) => path.split("/")[1])),
    new Set(PUBLIC_SLUGS.filter((slug) => slug !== "home")),
  );
});
test("brochure content has correct central contact details, package prices and distinct search metadata", () => {
  const brand = records.find((row) => row.kind === "brand").payload;
  assert.equal(brand.contact_phone, "+919000365219");
  assert.equal(brand.contact_email, "patnampakodi@gmail.com");
  assert.deepEqual(
    records
      .filter((row) => row.kind === "franchise")
      .map((row) => row.payload.investment_paise),
    [6900000, 9900000, 15000000, 30000000],
  );
  const pages = records
    .filter((row) => row.kind === "page" && PUBLIC_SLUGS.includes(row.slug))
    .map((row) => row.payload);
  for (const page of pages) {
    assert.ok(page.title.length <= 60, page.slug);
    assert.ok(page.description.length <= 160, page.slug);
  }
  assert.equal(new Set(pages.map((page) => page.title)).size, pages.length);
  assert.equal(
    new Set(pages.map((page) => page.description)).size,
    pages.length,
  );
});
