import test from "node:test";
import assert from "node:assert/strict";
import { normalizeCatalogQuery } from "../../src/lib/catalog-query.mjs";

test("catalog URL input preserves combined filters and rupee precision", () => {
  assert.deepEqual(
    normalizeCatalogQuery({
      q: " pepper ",
      category: "ready-mixes",
      tag: "spicy",
      dietary: "veg",
      max: "118.25",
      sort: "price-desc",
    }),
    {
      q: "pepper",
      category: "ready-mixes",
      tag: "spicy",
      dietary: "veg",
      max_price: 11825,
      sort: "price-desc",
    },
  );
});
test("untrusted URL input cannot escape query bounds or become server errors", () => {
  const result = normalizeCatalogQuery({
    q: "x".repeat(101),
    category: "x".repeat(81),
    tag: "../private",
    dietary: ["veg", "non-veg"],
    max: "Infinity",
    sort: "price_paise; DELETE",
  });
  assert.equal(result.q.length, 100);
  assert.equal(result.category, "");
  assert.equal(result.tag, "");
  assert.equal(result.dietary, "");
  assert.equal(result.max_price, undefined);
  assert.equal(result.sort, "default");
  assert.equal(normalizeCatalogQuery({ max: "0" }).max_price, 0);
  assert.equal(normalizeCatalogQuery({ max: "-1" }).max_price, undefined);
});
