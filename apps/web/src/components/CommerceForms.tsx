"use client";
import { SiteLink } from "@/components/SiteLink";
import { BrowserReady } from "./BrowserReady";

import { useEffect, useState, type FormEvent } from "react";
import { api, jsonPost, money, statusLabel, type Schema } from "@/lib/commerce";

type Cart = Schema["CartLine"][];
const CART_KEY = "pakodi-cart-v1";
function loadCart(): Cart {
  try {
    const data: unknown = JSON.parse(localStorage.getItem(CART_KEY) ?? "[]");
    return Array.isArray(data)
      ? data
          .filter(
            (item) =>
              typeof item?.variant_id === "string" &&
              Number.isInteger(item.quantity) &&
              item.quantity > 0 &&
              item.quantity <= 100,
          )
          .slice(0, 50)
      : [];
  } catch {
    return [];
  }
}
function saveCart(cart: Cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
}
export { Field, Notice } from "./FormFields";
import { Field, Notice } from "./FormFields";
export function AddToCart({
  variant,
  quantityInput = false,
}: {
  variant: Schema["VariantView"];
  quantityInput?: boolean;
}) {
  const [quantity, setQuantity] = useState("1");
  const [message, setMessage] = useState("");
  return (
    <>
      {quantityInput && (
        <label className="field">
          Quantity
          <input
            type="number"
            min={1}
            max={100}
            step={1}
            value={quantity}
            onChange={(event) => setQuantity(event.target.value)}
          />
        </label>
      )}
      <button
        className="button"
        disabled={variant.stock <= variant.reserved}
        onClick={() => {
          try {
            const cart = loadCart();
            const existing = cart.find(
              (line) => line.variant_id === variant.id,
            );
            const count = quantityInput ? Number(quantity) : 1;
            if (!Number.isInteger(count) || count < 1 || count > 100) {
              setMessage("Choose a quantity from 1 to 100.");
              return;
            }
            if (
              (existing?.quantity ?? 0) + count > 100 ||
              (!existing && cart.length >= 50)
            ) {
              setMessage(
                "Cart limit reached. Adjust the quantities in your cart.",
              );
              return;
            }
            if (existing) existing.quantity += count;
            else cart.push({ variant_id: variant.id, quantity: count });
            saveCart(cart);
            setMessage("Added to your cart.");
          } catch {
            setMessage("Allow browser storage to use the cart.");
          }
        }}
      >
        {variant.stock <= variant.reserved
          ? "Currently unavailable"
          : "Add to cart"}
      </button>
      <Notice message={message} />
    </>
  );
}

export function CartForm({ catalog }: { catalog: Schema["VariantView"][] }) {
  return (
    <BrowserReady>
      <LoadedCart catalog={catalog} />
    </BrowserReady>
  );
}
function LoadedCart({ catalog }: { catalog: Schema["VariantView"][] }) {
  const [cart, setCart] = useState<Cart>(loadCart);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [requestKey] = useState(() => crypto.randomUUID());
  function change(next: Cart) {
    setCart(next);
    try {
      saveCart(next);
    } catch {
      setMessage("Your browser could not save the cart.");
    }
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!cart?.length || busy) return;
    const form = new FormData(event.currentTarget);
    const customer = Object.fromEntries(
      ["name", "phone", "address", "city", "state_code", "pincode"].map(
        (key) => [key, String(form.get(key) ?? "")],
      ),
    ) as Schema["Address"];
    setBusy(true);
    setMessage("Saving your request…");
    try {
      const result = await api<Schema["RequestReceipt"]>(
        "orders",
        jsonPost({
          request_key: requestKey,
          customer,
          lines: cart,
          whatsapp_consent: form.get("consent") === "on",
        } satisfies Schema["OrderRequest"]),
      );
      change([]);
      window.location.assign("/track/#access=" + result.access_token);
    } catch (error) {
      setMessage((error as Error).message);
      setBusy(false);
    }
  }
  if (cart === null) return <Notice message="Loading your cart…" />;
  if (!cart.length)
    return (
      <div className="panel">
        <h2>Your cart is empty</h2>
        <p>Explore our packaged products to get started.</p>
        <SiteLink className="button" href="/shop/">
          Browse the shop
        </SiteLink>
      </div>
    );
  const unavailable = cart.some(
    (line) => !catalog.find((item) => item.id === line.variant_id),
  );
  return (
    <form onSubmit={submit} className="commerce-grid">
      <div className="panel">
        <h2>Your products</h2>
        {cart.map((line) => {
          const item = catalog.find(
            (variant) => variant.id === line.variant_id,
          );
          return (
            <div className="cart-row" key={line.variant_id}>
              <div>
                <h3>{item?.product.name ?? "Unavailable product"}</h3>
                <p>
                  {item
                    ? money(item.product.price_paise)
                    : "Remove this item to continue."}
                </p>
              </div>
              <Field
                name={line.variant_id}
                label={`Quantity for ${item?.product.name ?? "unavailable product"}`}
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
                              Math.min(100, Number(event.target.value)),
                            ),
                          }
                        : entry,
                    ),
                  )
                }
              />
              <button
                type="button"
                className="button button-small"
                onClick={() =>
                  change(
                    cart.filter(
                      (entry) => entry.variant_id !== line.variant_id,
                    ),
                  )
                }
              >
                Remove
              </button>
            </div>
          );
        })}
        <p>
          Product subtotal:{" "}
          <strong>
            {money(
              cart.reduce(
                (sum, line) =>
                  sum +
                  (catalog.find((item) => item.id === line.variant_id)?.product
                    .price_paise ?? 0) *
                    line.quantity,
                0,
              ),
            )}
          </strong>
        </p>
        <p>Delivery fee: confirmed by our team before payment.</p>
      </div>
      <div className="panel form-stack">
        <h2>Delivery request</h2>
        <p>
          We will confirm delivery availability and the final total. You pay
          only after approval.
        </p>
        <Field
          name="name"
          label="Full name"
          autoComplete="name"
          minLength={2}
          maxLength={100}
        />
        <Field
          name="phone"
          label="Phone including +91"
          type="tel"
          autoComplete="tel"
          pattern="\+91[6-9][0-9]{9}"
          placeholder="+919876543210"
        />
        <Field
          name="address"
          label="Street address"
          autoComplete="street-address"
          minLength={10}
          maxLength={500}
        />
        <Field
          name="city"
          label="City"
          autoComplete="address-level2"
          minLength={2}
          maxLength={100}
        />
        <label className="field">
          State
          <select name="state_code" required defaultValue="">
            <option value="" disabled>
              Select state
            </option>
            {Object.entries(STATES)
              .sort((a, b) => a[1].localeCompare(b[1]))
              .map(([code, name]) => (
                <option value={code} key={code}>
                  {name}
                </option>
              ))}
          </select>
        </label>
        <Field
          name="pincode"
          label="Pincode"
          autoComplete="postal-code"
          inputMode="numeric"
          pattern="[1-9][0-9]{5}"
        />
        <label className="checkbox">
          <input type="checkbox" name="consent" />
          Send order updates on WhatsApp to this number. I can stop them at any
          time.
        </label>
        <p className="small">
          Without WhatsApp updates, save your private order link to check
          approval and pay.
        </p>
        <button className="button" disabled={busy || unavailable}>
          {busy ? "Saving…" : "Request delivery"}
        </button>
        <Notice message={message} />
      </div>
    </form>
  );
}

const STATES: Record<string, string> = {
  "01": "Jammu and Kashmir",
  "02": "Himachal Pradesh",
  "03": "Punjab",
  "04": "Chandigarh",
  "05": "Uttarakhand",
  "06": "Haryana",
  "07": "Delhi",
  "08": "Rajasthan",
  "09": "Uttar Pradesh",
  "10": "Bihar",
  "11": "Sikkim",
  "12": "Arunachal Pradesh",
  "13": "Nagaland",
  "14": "Manipur",
  "15": "Mizoram",
  "16": "Tripura",
  "17": "Meghalaya",
  "18": "Assam",
  "19": "West Bengal",
  "20": "Jharkhand",
  "21": "Odisha",
  "22": "Chhattisgarh",
  "23": "Madhya Pradesh",
  "24": "Gujarat",
  "26": "Dadra and Nagar Haveli and Daman and Diu",
  "27": "Maharashtra",
  "29": "Karnataka",
  "30": "Goa",
  "31": "Lakshadweep",
  "32": "Kerala",
  "33": "Tamil Nadu",
  "34": "Puducherry",
  "35": "Andaman and Nicobar Islands",
  "36": "Telangana",
  "37": "Andhra Pradesh",
  "38": "Ladakh",
};

type RazorpayWindow = Window & {
  Razorpay?: new (options: {
    key: string;
    order_id: string;
    amount: number;
    currency: string;
    name: string;
    handler: () => void;
    modal: { ondismiss: () => void };
  }) => { open: () => void };
};
export function OrderManager({ nonce }: { nonce: string }) {
  return (
    <BrowserReady>
      <LoadedOrder nonce={nonce} />
    </BrowserReady>
  );
}
function LoadedOrder({ nonce }: { nonce: string }) {
  const [token] = useState(
    () =>
      new URLSearchParams(window.location.hash.slice(1)).get("access") ?? "",
  );
  const [order, setOrder] = useState<Schema["OrderView"] | null>(null);
  const [tracking, setTracking] = useState<Schema["TrackingStatus"] | null>(
    null,
  );
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [confirmCancel, setConfirmCancel] = useState(false);
  useEffect(() => {
    if (token)
      api<Schema["OrderView"]>("order", {
        headers: { Authorization: "Bearer " + token },
      })
        .then(setOrder)
        .catch((error) => setMessage(error.message));
  }, [token]);
  const auth = { Authorization: "Bearer " + token };
  async function refresh() {
    try {
      setOrder(await api<Schema["OrderView"]>("order", { headers: auth }));
      setMessage("Order status updated.");
    } catch (error) {
      setMessage((error as Error).message);
    }
  }
  async function pay() {
    if (!order) return;
    setBusy(true);
    setMessage("Preparing secure payment…");
    try {
      let checkout: Schema["PaymentCheckout"] | null = null;
      for (let attempt = 0; attempt < 10; attempt++) {
        checkout = await api<Schema["PaymentCheckout"]>("order/payment", {
          ...jsonPost({ quote_version: order.quote_version }),
          headers: auth,
        });
        if (checkout.order_id) break;
        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
      if (!checkout?.order_id)
        throw new Error(
          "Payment setup is taking longer than expected. Your request is saved; try again shortly.",
        );
      if (!(window as RazorpayWindow).Razorpay)
        await new Promise<void>((resolve, reject) => {
          const script = document.createElement("script");
          script.src = "https://checkout.razorpay.com/v1/checkout.js";
          script.nonce = nonce;
          script.onload = () => resolve();
          script.onerror = () =>
            reject(
              new Error("Secure payment could not load. Please try again."),
            );
          document.head.appendChild(script);
        });
      const Checkout = (window as RazorpayWindow).Razorpay;
      if (!Checkout) throw new Error("Payment could not load");
      new Checkout({
        key: checkout.key_id,
        order_id: checkout.order_id,
        amount: checkout.amount,
        currency: checkout.currency,
        name: "Patnam Pakodi",
        handler: () => {
          setMessage(
            "Payment submitted. We are checking confirmation; refresh the order shortly.",
          );
          setBusy(false);
          void refresh();
        },
        modal: {
          ondismiss: () => {
            setBusy(false);
            setMessage(
              "Payment window closed. Check the order status before retrying.",
            );
          },
        },
      }).open();
    } catch (error) {
      setMessage((error as Error).message);
      setBusy(false);
    }
  }
  async function downloadInvoice() {
    setBusy(true);
    try {
      const response = await fetch("/api/v1/order/invoice", {
        headers: auth,
        cache: "no-store",
      });
      if (!response.ok) throw new Error("Invoice is not available yet.");
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a");
      link.href = url;
      link.download = "invoice.pdf";
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function lookup(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setBusy(true);
    try {
      setTracking(
        await api<Schema["TrackingStatus"]>(
          "tracking",
          jsonPost({
            reference: data.get("reference"),
            phone: data.get("phone"),
          }),
        ),
      );
      setMessage("");
    } catch (error) {
      setTracking(null);
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Notice message={message} />
      {!token ? (
        <form className="panel form-stack narrow" onSubmit={lookup}>
          <p>
            Check basic status with your order number and phone. Use your
            private order link to pay, download an invoice, or cancel.
          </p>
          <Field
            name="reference"
            label="Order number"
            placeholder="PP-XXXXXXXXXX"
            pattern="PP-[0-9A-HJKMNP-TV-Z]{10}"
          />
          <Field
            name="phone"
            label="Phone including +91"
            type="tel"
            pattern="\+91[6-9][0-9]{9}"
          />
          <button className="button" disabled={busy}>
            Check status
          </button>
          {tracking && (
            <p role="status">
              {tracking.reference}: {statusLabel(tracking.status)}
            </p>
          )}
        </form>
      ) : !order ? (
        <p>
          Your private order details will appear here when available. Contact
          support if your link has expired.
        </p>
      ) : (
        <div className="commerce-grid">
          <section className="panel form-stack">
            <p className="eyebrow">{order.reference}</p>
            <h2>{statusLabel(order.status)}</h2>
            <p>Save this private link. Anyone with it can manage this order.</p>
            <div className="actions">
              <button
                className="button button-small"
                onClick={async () => {
                  try {
                    await navigator.clipboard.writeText(window.location.href);
                    setMessage("Private link copied.");
                  } catch {
                    setMessage("Copy this page’s address to save your link.");
                  }
                }}
              >
                Copy private link
              </button>
              <button className="button button-small" onClick={refresh}>
                Refresh status
              </button>
            </div>
            <p>
              {order.customer.name}
              <br />
              {order.customer.address}
              <br />
              {order.customer.city}, {order.customer.pincode}
            </p>
            {order.note && <p>{order.note}</p>}
            {order.consent && (
              <button
                className="button button-small"
                onClick={async () => {
                  try {
                    await api("order/opt-out", {
                      method: "POST",
                      headers: auth,
                    });
                    await refresh();
                    setMessage("WhatsApp updates stopped.");
                  } catch (error) {
                    setMessage((error as Error).message);
                  }
                }}
              >
                Stop WhatsApp updates
              </button>
            )}
          </section>
          <section className="panel form-stack">
            <h2>Order summary</h2>
            {order.lines.map((line) => (
              <p key={line.variant_id}>
                {line.quantity} × {line.name}
                <strong className="amount">
                  {money(line.price_paise * line.quantity)}
                </strong>
              </p>
            ))}
            <p>
              Delivery
              <strong className="amount">
                {order.quote_expires_at
                  ? money(order.delivery_paise)
                  : "To be confirmed"}
              </strong>
            </p>
            {order.total_paise > 0 && (
              <p>
                Total including tax
                <strong className="amount">{money(order.total_paise)}</strong>
              </p>
            )}
            {order.quote_expires_at && (
              <p className="small">
                Quote valid until{" "}
                {new Date(order.quote_expires_at).toLocaleString("en-IN")}.
              </p>
            )}
            {["approved", "payment_pending"].includes(order.status) && (
              <button className="button" disabled={busy} onClick={pay}>
                {busy ? "Preparing payment…" : "Pay securely"}
              </button>
            )}
            {order.invoice_number && (
              <button
                className="button button-small"
                disabled={busy}
                onClick={downloadInvoice}
              >
                Download invoice
              </button>
            )}
            {["requested", "approved", "payment_pending", "paid"].includes(
              order.status,
            ) &&
              (confirmCancel ? (
                <div className="notice">
                  <p>
                    Cancel this order? Any captured payment will be refunded
                    before dispatch.
                  </p>
                  <div className="actions">
                    <button
                      className="button button-small"
                      onClick={async () => {
                        try {
                          setOrder(
                            await api<Schema["OrderView"]>("order/cancel", {
                              method: "POST",
                              headers: auth,
                            }),
                          );
                          setConfirmCancel(false);
                        } catch (error) {
                          setMessage((error as Error).message);
                        }
                      }}
                    >
                      Confirm cancellation
                    </button>
                    <button
                      className="button button-small"
                      onClick={() => setConfirmCancel(false)}
                    >
                      Keep order
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  className="button button-small"
                  onClick={() => setConfirmCancel(true)}
                >
                  Cancel order
                </button>
              ))}
          </section>
        </div>
      )}
    </>
  );
}
