"use client";
import { SiteLink } from "@/components/SiteLink";
import { BrowserReady } from "./BrowserReady";

import { useEffect, useState, type FormEvent } from "react";
import { api, jsonPost, money, statusLabel, type Schema } from "@/lib/commerce";

export { AddToCart } from "./ProductActions";
import { Field, Notice } from "./FormFields";
import { ReorderButton } from "./ProductActions";
import { updateShopping } from "@/lib/shopping";
import { removePurchased } from "@/lib/shopping-state.mjs";
import { OrderTimeline } from "./OrderTimeline";

export const STATES: Record<string, string> = {
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
  const [fixtureQuote, setFixtureQuote] = useState<number | null>(null);
  useEffect(() => {
    if (token)
      api<Schema["OrderView"]>("order", {
        headers: { Authorization: "Bearer " + token },
      })
        .then(setOrder)
        .catch((error) => setMessage(error.message));
  }, [token]);
  useEffect(() => {
    if (!order || !order.invoice_number) return;
    try {
      const pending = JSON.parse(
        sessionStorage.getItem("pakodi-pending-checkout") ?? "null",
      );
      if (
        pending?.reference !== order.reference ||
        pending.mode !== order.shopping_mode ||
        !Array.isArray(pending.lines)
      )
        return;
      updateShopping((state) => ({
        ...state,
        carts: {
          ...state.carts,
          [order.shopping_mode]: removePurchased(
            state.carts[order.shopping_mode],
            pending.lines,
          ),
        },
      }));
      sessionStorage.removeItem("pakodi-pending-checkout");
    } catch {
      /* Keep the paid order usable even if storage is disabled. */
    }
  }, [order]);
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
      if (checkout.fixture) {
        setFixtureQuote(order.quote_version);
        setBusy(false);
        setMessage("Local test checkout is ready. No money will be charged.");
        return;
      }
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
  async function simulatePayment() {
    if (!order || fixtureQuote !== order.quote_version || busy) return;
    setBusy(true);
    try {
      const result = await api<Schema["ActionResult"]>(
        "order/fixture-capture",
        {
          ...jsonPost({ quote_version: fixtureQuote }),
          headers: auth,
        },
      );
      setMessage(result.detail);
      setFixtureQuote(null);
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
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
            <OrderTimeline order={order} />
            {order.shopping_mode === "fresh" && (
              <p>
                {String(order.fulfilment.outlet_name ?? "")}
                {order.fulfilment.preparation_minutes
                  ? ` · About ${order.fulfilment.preparation_minutes} minutes to prepare`
                  : ""}
              </p>
            )}
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
            {["preparing", "dispatched", "delivery_issue"].includes(
              order.status,
            ) && (
              <p>
                Need help with this order?{" "}
                <SiteLink href="/contact/">Contact our team</SiteLink>.
              </p>
            )}
            <ReorderButton order={order} />
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
            {order.quote_expires_at &&
              ["approved", "payment_pending"].includes(order.status) && (
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
            {fixtureQuote === order.quote_version &&
              ["approved", "payment_pending"].includes(order.status) && (
                <section
                  className="notice form-stack"
                  aria-label="Local test checkout"
                >
                  <h3>Simulate a payment</h3>
                  <p>
                    This local checkout uses a provider fixture. No money is
                    charged and no real message is sent.
                  </p>
                  <button
                    className="button"
                    disabled={busy}
                    onClick={simulatePayment}
                  >
                    Confirm test payment
                  </button>
                  <button
                    className="button button-small"
                    disabled={busy}
                    onClick={() => setFixtureQuote(null)}
                  >
                    Close test checkout
                  </button>
                </section>
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
                    Cancel this order? Any captured payment will be refunded.{" "}
                    {order.shopping_mode === "fresh"
                      ? "Cancellation is available until preparation starts."
                      : "Cancellation is available before dispatch."}
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
