export const SHOPPING_KEY = "pakodi-shopping-v2";
export const EMPTY_SHOPPING = JSON.stringify({
  mode: "packaged",
  carts: { packaged: [], fresh: [] },
  favourites: [],
});
export function cleanLines(value) {
  if (!Array.isArray(value)) return [];
  const lines = new Map();
  for (const item of value.slice(0, 50)) {
    if (
      typeof item?.variant_id !== "string" ||
      !/^[\da-f-]{36}$/i.test(item.variant_id) ||
      !Number.isInteger(item.quantity) ||
      item.quantity < 1 ||
      item.quantity > 100
    )
      continue;
    lines.set(item.variant_id, {
      variant_id: item.variant_id,
      quantity: item.quantity,
    });
  }
  return [...lines.values()];
}
export function parseShopping(raw) {
  let data;
  try {
    data = JSON.parse(raw);
  } catch {
    data = {};
  }
  return {
    mode: data?.mode === "fresh" ? "fresh" : "packaged",
    carts: {
      packaged: cleanLines(data?.carts?.packaged),
      fresh: cleanLines(data?.carts?.fresh),
    },
    favourites: Array.isArray(data?.favourites)
      ? [
          ...new Set(
            data.favourites.filter(
              (id) => typeof id === "string" && /^[\da-f-]{36}$/i.test(id),
            ),
          ),
        ].slice(0, 100)
      : [],
  };
}

export function mergeOrderLines(current, order, catalog) {
  const next = current.map((line) => ({ ...line }));
  for (const line of order.lines) {
    const item = catalog.find(
      (entry) =>
        entry.id === line.variant_id &&
        entry.product.mode === order.shopping_mode,
    );
    const existing = next.find((entry) => entry.variant_id === line.variant_id);
    const quantity = (existing?.quantity ?? 0) + line.quantity;
    if (!item || quantity > Math.min(100, item.stock - item.reserved))
      throw new Error(
        `${line.name} is not available in the requested quantity. Your existing cart is unchanged.`,
      );
    if (existing) existing.quantity = quantity;
    else next.push({ variant_id: line.variant_id, quantity });
  }
  if (next.length > 50)
    throw new Error(
      "Your cart has reached its limit. Review it before adding this order.",
    );
  return next;
}

export function removePurchased(current, purchased) {
  return current
    .map((line) => ({
      ...line,
      quantity:
        line.quantity -
        (purchased.find((entry) => entry.variant_id === line.variant_id)
          ?.quantity ?? 0),
    }))
    .filter((line) => line.quantity > 0);
}
