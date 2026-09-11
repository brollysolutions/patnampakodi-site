"use client";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { api, jsonPost, money, type Schema } from "@/lib/commerce";
import { useShopping, updateShopping, type ShoppingMode } from "@/lib/shopping";
import { Icon } from "./Icon";
import { SiteLink } from "./SiteLink";
import { ProductImage } from "./ProductImage";
import { ProductCard } from "./ProductCard";
import { DeliveryCheck } from "./DeliveryCheck";
import { Field, Notice } from "./FormFields";
import { STATES } from "./CommerceForms";
type Catalog = Schema["VariantView"][];
export function Basket({
  catalog,
  mode,
  checkout = false,
}: {
  catalog: Catalog;
  mode?: ShoppingMode;
  checkout?: boolean;
}) {
  const state = useShopping(),
    active = mode ?? state.mode,
    cart = state.carts[active];
  const [message, setMessage] = useState(""),
    [removed, setRemoved] = useState<Schema["CartLine"] | null>(null);
  useEffect(() => {
    if (mode && mode !== state.mode) {
      try {
        updateShopping((current) => ({ ...current, mode }));
      } catch {
        /* The URL keeps this basket usable when storage is unavailable. */
      }
    }
  }, [mode, state.mode]);
  const subtotal = cart.reduce(
    (sum, line) =>
      sum +
      (catalog.find((item) => item.id === line.variant_id)?.product
        .price_paise ?? 0) *
        line.quantity,
    0,
  );
  const unavailable = cart.some((line) => {
    const item = catalog.find((item) => item.id === line.variant_id);
    return (
      !item ||
      item.product.mode !== active ||
      item.stock - item.reserved < line.quantity
    );
  });
  const change = (lines: Schema["CartLine"][]) => {
    try {
      updateShopping((current) => ({
        ...current,
        mode: active,
        carts: { ...current.carts, [active]: lines },
      }));
      setMessage("");
    } catch {
      setMessage(
        "Your browser could not save the cart. Allow browser storage and try again.",
      );
    }
  };
  return (
    <>
      <nav className="basket-modes" aria-label="Your baskets">
        {(["fresh", "packaged"] as const).map((value) => (
          <SiteLink
            key={value}
            href={`/${checkout ? "checkout" : "cart"}/?mode=${value}`}
            className={`button button-outline ${active === value ? "is-selected" : ""}`}
            aria-current={active === value ? "page" : undefined}
            onClick={() => {
              try {
                updateShopping((current) => ({ ...current, mode: value }));
              } catch {
                /* The URL retains the chosen mode. */
              }
            }}
          >
            <Icon name={value === "fresh" ? "fresh" : "box"} />
            {value === "fresh" ? "Fresh food" : "Packaged"} (
            {state.carts[value].reduce((sum, line) => sum + line.quantity, 0)})
          </SiteLink>
        ))}
      </nav>
      <Notice message={message} />
      {!cart.length ? (
        <div className="store-empty">
          <Icon name="bag" />
          <h2>Your cart is empty</h2>
          <p>
            {active === "fresh"
              ? "Find something crisp, spicy and made for your next snack break."
              : "Bring your favourite flavours home. Explore our packaged range."}
          </p>
          <SiteLink
            className="button"
            href={active === "fresh" ? "/menu/" : "/shop/"}
          >
            Browse {active === "fresh" ? "fresh food" : "the shop"}
            <Icon name="arrow" />
          </SiteLink>
          {removed && (
            <button
              className="text-link"
              onClick={() => {
                change([removed]);
                setRemoved(null);
              }}
            >
              Undo removal
            </button>
          )}
        </div>
      ) : checkout ? (
        <CheckoutFlow
          key={active}
          mode={active}
          cart={cart}
          catalog={catalog}
          unavailable={unavailable}
        />
      ) : (
        <div className="checkout-layout">
          <div>
            <div className="panel">
              <h2>
                {active === "fresh" ? "Your fresh picks" : "Your pantry picks"}
              </h2>
              {cart.map((line) => {
                const item = catalog.find(
                  (item) => item.id === line.variant_id,
                );
                return (
                  <article className="basket-row" key={line.variant_id}>
                    {item ? (
                      <ProductImage variant={item} />
                    ) : (
                      <Icon name="box" />
                    )}
                    <div>
                      <h3>
                        {item ? (
                          <a href={`/product/${item.product.slug}/`}>
                            {item.product.name}
                          </a>
                        ) : (
                          "Unavailable product"
                        )}
                      </h3>
                      <p>
                        {item
                          ? `${item.product.net_quantity} · ${money(item.product.price_paise * line.quantity)}`
                          : "Remove this item to continue."}
                      </p>
                      {item && line.quantity > item.stock - item.reserved && (
                        <p role="alert">
                          Only {Math.max(0, item.stock - item.reserved)}{" "}
                          available. Adjust the quantity to continue.
                        </p>
                      )}
                      <div className="basket-row-actions">
                        <div className="quantity-stepper">
                          <button
                            aria-label={`Decrease quantity for ${item?.product.name ?? "product"}`}
                            disabled={line.quantity === 1}
                            onClick={() =>
                              change(
                                cart.map((entry) =>
                                  entry.variant_id === line.variant_id
                                    ? { ...entry, quantity: entry.quantity - 1 }
                                    : entry,
                                ),
                              )
                            }
                          >
                            <Icon name="minus" />
                          </button>
                          <label>
                            <span className="sr-only">
                              Quantity for{" "}
                              {item?.product.name ?? "unavailable product"}
                            </span>
                            <input
                              type="number"
                              min={1}
                              max={100}
                              value={line.quantity}
                              onChange={(event) =>
                                change(
                                  cart.map((entry) =>
                                    entry.variant_id === line.variant_id
                                      ? {
                                          ...entry,
                                          quantity: Math.max(
                                            1,
                                            Math.min(
                                              100,
                                              Math.trunc(
                                                Number(event.target.value) || 1,
                                              ),
                                            ),
                                          ),
                                        }
                                      : entry,
                                  ),
                                )
                              }
                            />
                          </label>
                          <button
                            aria-label={`Increase quantity for ${item?.product.name ?? "product"}`}
                            disabled={
                              line.quantity >=
                              Math.min(
                                100,
                                item ? item.stock - item.reserved : 0,
                              )
                            }
                            onClick={() =>
                              change(
                                cart.map((entry) =>
                                  entry.variant_id === line.variant_id
                                    ? { ...entry, quantity: entry.quantity + 1 }
                                    : entry,
                                ),
                              )
                            }
                          >
                            <Icon name="plus" />
                          </button>
                        </div>
                        <button
                          className="text-link"
                          onClick={() => {
                            setRemoved(line);
                            change(
                              cart.filter(
                                (entry) => entry.variant_id !== line.variant_id,
                              ),
                            );
                          }}
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
            {removed && (
              <p className="undo-removal" role="status">
                Item removed.{" "}
                <button
                  className="text-link"
                  onClick={() => {
                    if (
                      !cart.some(
                        (line) => line.variant_id === removed.variant_id,
                      )
                    )
                      change([...cart, removed]);
                    setRemoved(null);
                  }}
                >
                  Undo
                </button>
              </p>
            )}
            <SiteLink
              className="text-link"
              href={active === "fresh" ? "/menu/" : "/shop/"}
            >
              Continue shopping
              <Icon name="arrow" />
            </SiteLink>
          </div>
          <aside className="checkout-summary form-stack">
            <div className="panel form-stack">
              <h2>Order summary</h2>
              <div className="summary-lines">
                <p>
                  <span>Products</span>
                  <strong>{money(subtotal)}</strong>
                </p>
                <p>
                  <span>Delivery</span>
                  <span>Calculated at checkout</span>
                </p>
                <p className="summary-total">
                  <span>Subtotal</span>
                  <strong>{money(subtotal)}</strong>
                </p>
              </div>
              <p className="summary-note">
                Product prices include applicable tax. Review the full total
                before payment.
              </p>
              {unavailable ? (
                <p role="alert">Update unavailable items before checkout.</p>
              ) : (
                <SiteLink href={`/checkout/?mode=${active}`} className="button">
                  Continue to checkout
                  <Icon name="arrow" />
                </SiteLink>
              )}
              <p className="summary-note">
                <Icon name="shield" /> Secure payment · Guest checkout
              </p>
            </div>
            <DeliveryCheck mode={active} />
          </aside>
        </div>
      )}
    </>
  );
}
function CheckoutFlow({
  mode,
  cart,
  catalog,
  unavailable,
}: {
  mode: ShoppingMode;
  cart: Schema["CartLine"][];
  catalog: Catalog;
  unavailable: boolean;
}) {
  const [quote, setQuote] = useState<Schema["CheckoutQuote"] | null>(null),
    [customer, setCustomer] = useState<Schema["Address"] | null>(null),
    [consent, setConsent] = useState(false),
    [busy, setBusy] = useState(false),
    [message, setMessage] = useState("");
  const detailsForm = useRef<HTMLFormElement>(null),
    returnToDetails = useRef(false);
  const key = useRef<string | null>(null),
    reviewHeading = useRef<HTMLHeadingElement>(null);
  const [reviewedCart, setReviewedCart] = useState("");
  useEffect(() => {
    if (quote) reviewHeading.current?.focus();
    else if (returnToDetails.current) {
      detailsForm.current?.querySelector("input")?.focus();
      returnToDetails.current = false;
    }
  }, [quote]);
  const changed = Boolean(quote && reviewedCart !== JSON.stringify(cart));
  async function review(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const details = Object.fromEntries(
      ["name", "phone", "address", "city", "state_code", "pincode"].map(
        (name) => [name, String(form.get(name) ?? "").trim()],
      ),
    ) as Schema["Address"];
    details.phone = details.phone.replace(/[\s()-]/g, "");
    if (/^[6-9][0-9]{9}$/.test(details.phone))
      details.phone = "+91" + details.phone;
    setBusy(true);
    setMessage("");
    setCustomer(details);
    setConsent(form.get("consent") === "on");
    try {
      const result = await api<Schema["CheckoutQuote"]>(
        "checkout/quote",
        jsonPost({
          mode,
          customer: details,
          lines: cart,
        } satisfies Schema["CheckoutQuoteRequest"]),
      );
      key.current = crypto.randomUUID();
      setReviewedCart(JSON.stringify(cart));
      setQuote(result);
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function place() {
    if (!quote || !customer || busy || changed) return;
    if (new Date(quote.expires_at).getTime() <= Date.now()) {
      setMessage("Your checkout review expired. Review the total again.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const receipt = await api<Schema["RequestReceipt"]>(
        "checkout/orders",
        jsonPost({
          mode,
          customer,
          lines: cart,
          quote_token: quote.quote_token,
          request_key: key.current!,
          whatsapp_consent: consent,
        } satisfies Schema["CheckoutOrderRequest"]),
      );
      try {
        sessionStorage.setItem(
          "pakodi-pending-checkout",
          JSON.stringify({ reference: receipt.reference, mode, lines: cart }),
        );
      } catch {
        /* The order link remains usable without session storage. */
      }
      window.location.assign("/track/#access=" + receipt.access_token);
    } catch (error) {
      setMessage((error as Error).message);
      setBusy(false);
    }
  }
  const subtotal = cart.reduce(
    (sum, line) =>
      sum +
      (catalog.find((item) => item.id === line.variant_id)?.product
        .price_paise ?? 0) *
        line.quantity,
    0,
  );
  return (
    <>
      <ol className="checkout-steps" aria-label="Checkout progress">
        <li aria-current={!quote ? "step" : undefined}>
          <b>1</b>Delivery
        </li>
        <li aria-current={quote ? "step" : undefined}>
          <b>2</b>Review
        </li>
        <li>
          <b>3</b>Payment
        </li>
      </ol>
      <div className="checkout-layout">
        <div>
          <form
            className="panel form-stack"
            onSubmit={review}
            ref={detailsForm}
            hidden={Boolean(quote)}
          >
            <h2>Where should we deliver?</h2>
            <p className="summary-note">
              No account needed. Your details are used to fulfil your order.
            </p>
            <div className="address-grid">
              <Field
                name="name"
                label="Full name"
                autoComplete="name"
                minLength={2}
                maxLength={100}
              />
              <Field
                name="phone"
                label="Phone number"
                type="tel"
                autoComplete="tel"
                placeholder="10-digit mobile or +91"
                minLength={10}
                maxLength={18}
              />
              <div className="full-width">
                <Field
                  name="address"
                  label="Street address"
                  autoComplete="street-address"
                  minLength={10}
                  maxLength={500}
                />
              </div>
              <Field
                name="city"
                label="City"
                autoComplete="address-level2"
                minLength={2}
                maxLength={100}
              />
              <Field
                name="pincode"
                label="PIN code"
                autoComplete="postal-code"
                inputMode="numeric"
                pattern="[1-9][0-9]{5}"
                maxLength={6}
              />
              <label className="field full-width">
                State
                <select name="state_code" required defaultValue="">
                  <option value="" disabled>
                    Select state
                  </option>
                  {Object.entries(STATES)
                    .sort((a, b) => a[1].localeCompare(b[1]))
                    .map(([code, name]) => (
                      <option key={code} value={code}>
                        {name}
                      </option>
                    ))}
                </select>
              </label>
            </div>
            <label className="checkbox">
              <input name="consent" type="checkbox" />
              Send order updates on WhatsApp. I can stop them at any time.
            </label>
            <p className="summary-note">
              You’ll also receive a private link here to manage your order.
            </p>
            <button className="button" disabled={busy || unavailable}>
              {busy ? "Checking your order…" : "Review order"}
              <Icon name="arrow" />
            </button>
          </form>
          {quote && customer && (
            <section className="panel form-stack">
              <h2 tabIndex={-1} ref={reviewHeading}>
                Everything look good?
              </h2>
              <div>
                <h3>Deliver to</h3>
                <p>
                  {customer.name}
                  <br />
                  {customer.address}
                  <br />
                  {customer.city}, {customer.pincode}
                  <br />
                  {customer.phone}
                </p>
              </div>
              {quote.fulfilment.outlet_name && (
                <p>
                  <Icon name="fresh" /> {quote.fulfilment.outlet_name}
                  {quote.fulfilment.preparation_minutes
                    ? ` · About ${quote.fulfilment.preparation_minutes} minutes to prepare`
                    : ""}
                </p>
              )}
              <p className="summary-note">
                {mode === "fresh"
                  ? "You can cancel until preparation starts. After that, contact our team for help."
                  : "You can cancel before dispatch through your private order link."}
              </p>
              <p className="summary-note">
                Review valid until{" "}
                {new Date(quote.expires_at).toLocaleTimeString("en-IN", {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
                . Availability is checked again before payment.
              </p>
              {changed && (
                <p role="alert">
                  Your cart changed. Review the updated order before continuing.
                </p>
              )}
              <button
                className="button"
                disabled={busy || changed}
                onClick={place}
              >
                {busy
                  ? "Preparing your order…"
                  : `Continue to payment · ${money(quote.total_paise)}`}
                <Icon name="shield" />
              </button>
              <button
                className="text-link"
                disabled={busy}
                onClick={() => {
                  returnToDetails.current = true;
                  setQuote(null);
                  setMessage("");
                }}
              >
                Edit details or refresh total
              </button>
            </section>
          )}
          <Notice message={message} />
          <SiteLink className="text-link" href={`/cart/?mode=${mode}`}>
            Return to cart
          </SiteLink>
        </div>
        <aside className="panel checkout-summary form-stack">
          <h2>Your order</h2>
          {cart.map((line) => {
            const item = catalog.find((item) => item.id === line.variant_id);
            return (
              <div className="basket-row" key={line.variant_id}>
                {item ? <ProductImage variant={item} /> : <Icon name="box" />}
                <div>
                  <h3>{item?.product.name ?? "Unavailable product"}</h3>
                  <p>
                    {line.quantity} ×{" "}
                    {item ? money(item.product.price_paise) : "Unavailable"}
                  </p>
                </div>
              </div>
            );
          })}
          <div className="summary-lines">
            <p>
              <span>Products</span>
              <strong>
                {money(
                  quote ? quote.total_paise - quote.delivery_paise : subtotal,
                )}
              </strong>
            </p>
            <p>
              <span>Delivery</span>
              <span>
                {quote ? money(quote.delivery_paise) : "After address check"}
              </span>
            </p>
            <p className="summary-total">
              <span>{quote ? "Total" : "Subtotal"}</span>
              <strong>{money(quote?.total_paise ?? subtotal)}</strong>
            </p>
          </div>
          <p className="summary-note">
            Including applicable tax. Payment confirmation appears after the
            payment provider verifies your transaction.
          </p>
        </aside>
      </div>
    </>
  );
}
export function Favourites({ catalog }: { catalog: Catalog }) {
  const state = useShopping(),
    items = catalog.filter((item) => state.favourites.includes(item.id));
  return (
    <>
      <p className="page-description">
        Keep the good ones close. Favourites are saved on this device.
      </p>
      {!items.length ? (
        <div className="store-empty">
          <Icon name="heart" />
          <h2>Your next favourite is waiting.</h2>
          <p>Tap the heart on a product to save it here.</p>
          <SiteLink href="/shop/" className="button">
            Explore the shop
            <Icon name="arrow" />
          </SiteLink>
        </div>
      ) : (
        (["fresh", "packaged"] as const).map((mode) => {
          const group = items.filter((item) => item.product.mode === mode);
          return group.length ? (
            <section className="store-section" key={mode}>
              <div className="store-section-heading">
                <h2>
                  {mode === "fresh" ? "Fresh favourites" : "Pantry favourites"}
                </h2>
                <SiteLink href={mode === "fresh" ? "/menu/" : "/shop/"}>
                  Explore more
                </SiteLink>
              </div>
              <div className="store-product-grid home-products">
                {group.map((item) => (
                  <ProductCard key={item.id} item={item} />
                ))}
              </div>
            </section>
          ) : null;
        })
      )}
      {state.favourites.length > items.length && (
        <p className="summary-note">
          Some saved products are no longer available.
        </p>
      )}
    </>
  );
}
