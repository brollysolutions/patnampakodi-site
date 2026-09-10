import test from "node:test";
import assert from "node:assert/strict";
import {
  indexable,
  isPrivatePath,
  serializeJsonLd,
  filterMenu,
  filterOutlets,
} from "../../src/lib/policy.mjs";

test("indexing requires an explicit public deployment opt-in", () => {
  assert.equal(indexable({ NODE_ENV: "production" }), false);
  assert.equal(
    indexable({ SITE_INDEXABLE: "true", DEPLOYMENT_ENV: "preview" }),
    false,
  );
  assert.equal(indexable({ SITE_INDEXABLE: "true" }), true);
  for (const path of [
    "/admin/orders/",
    "/account/",
    "/checkout/",
    "/api/content/",
  ])
    assert.ok(isPrivatePath(path));
  assert.equal(isPrivatePath("/franchise/"), false);
});

test("editorial JSON cannot terminate a structured data script", () => {
  const source = { name: '</script><script>alert("x")</script>' };
  const serialized = serializeJsonLd(source);
  assert.equal(serialized.includes("<"), false);
  assert.deepEqual(JSON.parse(serialized), source);
});

test("menu search combines category and case-insensitive words", () => {
  const items = [
    { name: "Kaju Chicken", description: "", category: "Dry" },
    { name: "Chicken Bowl", description: "", category: "Bowls" },
  ];
  assert.deepEqual(filterMenu(items, "Dry", " CHICKEN "), [items[0]]);
  assert.deepEqual(filterMenu(items, "Drinks", "Chicken"), []);
});

test("outlets can be found by locality or pincode", () => {
  const outlets = [{ name: "Madhapur", city: "Hyderabad", pincode: "500081" }];
  assert.equal(filterOutlets(outlets, " MADHAPUR ").length, 1);
  assert.equal(filterOutlets(outlets, "500081").length, 1);
  assert.equal(filterOutlets(outlets, "000000").length, 0);
});
