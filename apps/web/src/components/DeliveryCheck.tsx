"use client";
import { useId, useState, type FormEvent } from "react";
import { api, money, type Schema } from "@/lib/commerce";
import type { ShoppingMode } from "@/lib/shopping";
import { Icon } from "./Icon";
export function DeliveryCheck({ mode }: { mode: ShoppingMode }) {
  const inputId = useId();
  const [result, setResult] = useState<Schema["Serviceability"] | null>(null),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  async function check(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    const pin = String(new FormData(event.currentTarget).get("delivery_pin"));
    try {
      setResult(
        await api<Schema["Serviceability"]>(
          `serviceability?mode=${mode}&pincode=${encodeURIComponent(pin)}`,
        ),
      );
    } catch (error) {
      setResult(null);
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="delivery-check" aria-label="Delivery availability">
      <div className="delivery-check-heading">
        <Icon name="pin" />
        <div>
          <strong>
            {mode === "fresh"
              ? "Fresh from your local kitchen"
              : "Your favourites, delivered"}
          </strong>
          <p>Check delivery to your PIN code.</p>
        </div>
      </div>
      <form onSubmit={check}>
        <label className="sr-only" htmlFor={inputId}>
          Delivery PIN code
        </label>
        <input
          id={inputId}
          name="delivery_pin"
          required
          inputMode="numeric"
          pattern="[1-9][0-9]{5}"
          maxLength={6}
          placeholder="6-digit PIN code"
        />
        <button className="button button-small button-outline" disabled={busy}>
          {busy ? "Checking…" : "Check"}
        </button>
      </form>
      <div role="status" aria-live="polite">
        {message ||
          (result && (
            <>
              <p className={result.available ? "delivery-available" : ""}>
                {result.message}
                {result.available && result.delivery_paise !== null
                  ? ` Delivery: ${money(result.delivery_paise)}.`
                  : ""}
              </p>
              {result.outlet_name && (
                <p>
                  {result.outlet_name}
                  {result.preparation_minutes
                    ? ` · About ${result.preparation_minutes} minutes to prepare`
                    : ""}
                </p>
              )}
              {!result.available && result.hours.length > 0 && (
                <details>
                  <summary>Kitchen hours</summary>
                  <ul>
                    {result.hours.map((window, index) => (
                      <li key={index}>
                        {
                          ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][
                            window.day
                          ]
                        }{" "}
                        {window.opens}–{window.closes} IST
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </>
          ))}
      </div>
    </section>
  );
}
