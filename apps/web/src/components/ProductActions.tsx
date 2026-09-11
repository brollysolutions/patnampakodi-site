"use client";
import { useState } from "react";
import { Icon } from "./Icon";
import { Notice } from "./FormFields";
import { useShopping, updateShopping } from "@/lib/shopping";
import { api, type Schema } from "@/lib/commerce";
import { mergeOrderLines } from "@/lib/shopping-state.mjs";
export function FavouriteButton({
  variant,
}: {
  variant: Schema["VariantView"];
}) {
  const state = useShopping(),
    selected = state.favourites.includes(variant.id);
  const [message, setMessage] = useState("");
  return (
    <>
      <button
        className="icon-button favourite-button"
        aria-label={`${selected ? "Remove" : "Save"} ${variant.product.name} ${selected ? "from" : "to"} favourites`}
        aria-pressed={selected}
        onClick={() => {
          try {
            updateShopping((current) => ({
              ...current,
              favourites: selected
                ? current.favourites.filter((id) => id !== variant.id)
                : [...current.favourites, variant.id].slice(-100),
            }));
            setMessage("");
          } catch {
            setMessage("Allow browser storage to save favourites.");
          }
        }}
      >
        <Icon name="heart" fill={selected ? "currentColor" : "none"} />
      </button>
      <Notice message={message} />
    </>
  );
}
export function AddToCart({
  variant,
  quantityInput = false,
}: {
  variant: Schema["VariantView"];
  quantityInput?: boolean;
}) {
  const [quantity, setQuantity] = useState(1),
    [message, setMessage] = useState("");
  const available = Math.max(0, variant.stock - variant.reserved);
  return (
    <div className="product-action">
      <div className="product-add-row">
        {quantityInput && (
          <div className="quantity-stepper">
            <button
              type="button"
              aria-label="Decrease quantity"
              disabled={quantity <= 1}
              onClick={() => setQuantity(quantity - 1)}
            >
              <Icon name="minus" />
            </button>
            <label>
              <span className="sr-only">Quantity</span>
              <input
                type="number"
                min={1}
                max={Math.min(100, available)}
                value={quantity}
                onChange={(event) => setQuantity(Number(event.target.value))}
              />
            </label>
            <button
              type="button"
              aria-label="Increase quantity"
              disabled={quantity >= Math.min(100, available)}
              onClick={() => setQuantity(quantity + 1)}
            >
              <Icon name="plus" />
            </button>
          </div>
        )}
        <button
          className="button"
          disabled={!available}
          onClick={() => {
            if (!Number.isInteger(quantity) || quantity < 1 || quantity > 100) {
              setMessage("Choose a quantity from 1 to 100.");
              return;
            }
            try {
              updateShopping((current) => {
                const mode = variant.product.mode;
                const cart = [...current.carts[mode]];
                const existing = cart.find(
                  (line) => line.variant_id === variant.id,
                );
                const total = (existing?.quantity ?? 0) + quantity;
                if (total > Math.min(available, 100))
                  throw new Error(
                    "That quantity is not available. Check your cart.",
                  );
                if (!existing && cart.length >= 50)
                  throw new Error(
                    "Cart limit reached. Adjust your cart to continue.",
                  );
                const next = existing
                  ? cart.map((line) =>
                      line.variant_id === variant.id
                        ? { ...line, quantity: total }
                        : line,
                    )
                  : [...cart, { variant_id: variant.id, quantity }];
                return {
                  ...current,
                  mode,
                  carts: { ...current.carts, [mode]: next },
                };
              });
              setMessage("Added to your cart.");
            } catch (error) {
              setMessage(
                error instanceof Error
                  ? error.message
                  : "Allow browser storage to use the cart.",
              );
            }
          }}
        >
          <Icon name={available ? "plus" : "clock"} />
          {available ? "Add to cart" : "Currently unavailable"}
        </button>
      </div>
      <Notice message={message} />
    </div>
  );
}
export function ReorderButton({ order }: { order: Schema["OrderView"] }) {
  const [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  return (
    <>
      <button
        className="button button-small button-outline"
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          setMessage("");
          try {
            const catalog = await api<Schema["VariantView"][]>("catalog");
            updateShopping((state) => ({
              ...state,
              mode: order.shopping_mode,
              carts: {
                ...state.carts,
                [order.shopping_mode]: mergeOrderLines(
                  state.carts[order.shopping_mode],
                  order,
                  catalog,
                ),
              },
            }));
            window.location.assign(`/cart/?mode=${order.shopping_mode}`);
          } catch (error) {
            setMessage(
              error instanceof Error
                ? error.message
                : "Your browser could not save this basket.",
            );
            setBusy(false);
          }
        }}
      >
        <Icon name="bag" />
        {busy ? "Checking availability..." : "Order again"}
      </button>
      <p className="small">
        Adds to your cart at current prices. Review delivery and availability
        again at checkout.
      </p>
      <Notice message={message} />
    </>
  );
}
