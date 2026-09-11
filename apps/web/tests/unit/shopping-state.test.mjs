import { test } from "node:test";
import assert from "node:assert/strict";
import {
  parseShopping,
  cleanLines,
  mergeOrderLines,
  removePurchased,
} from "../../src/lib/shopping-state.mjs";
const a = "11111111-1111-4111-8111-111111111111",
  b = "22222222-2222-4222-8222-222222222222";
test("corrupt browser storage and malformed quantities do not enter the cart", () => {
  assert.deepEqual(parseShopping("broken").carts, { fresh: [], packaged: [] });
  assert.deepEqual(
    cleanLines([
      { variant_id: a, quantity: 0 },
      { variant_id: b, quantity: 2.5 },
      { variant_id: "invalid", quantity: 1 },
    ]),
    [],
  );
  assert.deepEqual(
    parseShopping(
      JSON.stringify({
        mode: "fresh",
        favourites: [a, a, "invalid"],
        carts: { fresh: [{ variant_id: a, quantity: 2 }] },
      }),
    ),
    {
      mode: "fresh",
      favourites: [a],
      carts: { fresh: [{ variant_id: a, quantity: 2 }], packaged: [] },
    },
  );
});
test("ordering again merges a complete order without losing an existing cart", () => {
  const existing = [{ variant_id: b, quantity: 2 }],
    order = {
      shopping_mode: "fresh",
      lines: [{ variant_id: a, quantity: 2, name: "Fresh fixture" }],
    },
    catalog = [{ id: a, product: { mode: "fresh" }, stock: 3, reserved: 0 }];
  assert.deepEqual(mergeOrderLines(existing, order, catalog), [
    ...existing,
    { variant_id: a, quantity: 2 },
  ]);
  assert.deepEqual(existing, [{ variant_id: b, quantity: 2 }]);
  assert.throws(
    () => mergeOrderLines([{ variant_id: a, quantity: 2 }], order, catalog),
    /not available/,
  );
  assert.throws(
    () =>
      mergeOrderLines(existing, order, [
        { ...catalog[0], product: { mode: "packaged" } },
      ]),
    /not available/,
  );
});
test("confirmed payment removes purchased quantities and retains subsequent additions", () => {
  const cart = [
    { variant_id: a, quantity: 3 },
    { variant_id: b, quantity: 1 },
  ];
  assert.deepEqual(removePurchased(cart, [{ variant_id: a, quantity: 2 }]), [
    { variant_id: a, quantity: 1 },
    { variant_id: b, quantity: 1 },
  ]);
  assert.deepEqual(removePurchased(cart, [{ variant_id: a, quantity: 3 }]), [
    { variant_id: b, quantity: 1 },
  ]);
  assert.equal(cart[0].quantity, 3);
});
