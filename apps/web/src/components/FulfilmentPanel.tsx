"use client";
import { useEffect, useState, type FormEvent } from "react";
import { api, type Schema } from "@/lib/commerce";
import { Field, Notice } from "./FormFields";
import { Icon } from "./Icon";
import { STATES } from "./CommerceForms";
const DAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];
type Settings = Schema["FulfilmentSettings-Output"];
export function FulfilmentPanel() {
  const [settings, setSettings] = useState<Settings | null>(null),
    [outlets, setOutlets] = useState<Schema["Outlet"][]>([]),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    let active = true;
    Promise.all([
      api<Settings>("admin/fulfilment"),
      api<Schema["Storefront"]>("storefront"),
    ])
      .then(([settings, content]) => {
        if (active) {
          setSettings(settings);
          setOutlets(content.outlets);
        }
      })
      .catch((error) => {
        if (active) setMessage(error.message);
      });
    return () => {
      active = false;
    };
  }, [revision]);
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!settings) return;
    setBusy(true);
    setMessage("");
    try {
      setSettings(
        await api<Settings>("admin/fulfilment", {
          method: "PUT",
          body: JSON.stringify(settings),
        }),
      );
      setMessage(
        "Delivery settings saved. New checkouts use these rules immediately.",
      );
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  if (!settings)
    return (
      <div className="panel">
        <Notice message={message || "Loading delivery settings…"} />
        {message && (
          <button className="button" onClick={() => setRevision(revision + 1)}>
            Try again
          </button>
        )}
      </div>
    );
  const change = (value: Partial<Settings>) =>
    setSettings({ ...settings, ...value });
  return (
    <form className="form-stack" onSubmit={save}>
      <div className="section-heading">
        <div>
          <p className="eyebrow">Ordering operations</p>
          <h2>Delivery &amp; fresh food</h2>
          <p>
            Control availability, preparation time and the delivery fee for each
            PIN code.
          </p>
        </div>
      </div>
      <fieldset className="form-stack" disabled={busy}>
        <legend className="sr-only">Delivery settings</legend>
        <section className="panel form-stack">
          <h3>
            <Icon name="box" /> Packaged ordering
          </h3>
          <label className="checkbox">
            <input
              type="checkbox"
              checked={settings.packaged_enabled}
              onChange={(event) =>
                change({ packaged_enabled: event.target.checked })
              }
            />
            Accept packaged orders online
          </label>
          <p className="small">
            A matching PIN rule, approved seller details and available stock are
            also required.
          </p>
        </section>
        <section className="panel form-stack">
          <h3>
            <Icon name="fresh" /> Fresh ordering
          </h3>
          <div className="actions">
            <label className="checkbox">
              <input
                type="checkbox"
                checked={settings.fresh_enabled}
                onChange={(event) =>
                  change({ fresh_enabled: event.target.checked })
                }
              />
              Enable fresh ordering
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={settings.fresh_paused}
                onChange={(event) =>
                  change({ fresh_paused: event.target.checked })
                }
              />
              Pause new fresh orders
            </label>
          </div>
          <div className="address-grid">
            <label className="field">
              Pilot outlet
              <select
                value={settings.outlet_slug}
                onChange={(event) =>
                  change({ outlet_slug: event.target.value })
                }
                required={settings.fresh_enabled}
              >
                <option value="">Choose a published outlet</option>
                {outlets.map((outlet) => (
                  <option key={outlet.slug} value={outlet.slug}>
                    {outlet.name}
                  </option>
                ))}
              </select>
            </label>
            <Field
              label="Preparation estimate in minutes"
              name="preparation"
              type="number"
              min={1}
              max={240}
              required={settings.fresh_enabled}
              value={settings.preparation_minutes ?? ""}
              onChange={(event) =>
                change({
                  preparation_minutes: event.target.value
                    ? Number(event.target.value)
                    : null,
                })
              }
            />
          </div>
          <p className="small">
            Fresh orders are for as-soon-as-possible delivery from this outlet.
            Pausing does not cancel orders already being handled.
          </p>
          <h4>Weekly opening hours · India Standard Time</h4>
          <p className="small">
            Days without a window are closed. Use 24:00 for midnight; split
            overnight hours across two days.
          </p>
          {settings.hours.length === 0 && <p>No opening windows added.</p>}
          {settings.hours.map((window, index) => (
            <div className="delivery-rule" key={index}>
              <label className="field">
                Day
                <select
                  value={window.day}
                  onChange={(event) =>
                    change({
                      hours: settings.hours.map((entry, i) =>
                        i === index
                          ? { ...entry, day: Number(event.target.value) }
                          : entry,
                      ),
                    })
                  }
                >
                  {DAYS.map((day, value) => (
                    <option key={day} value={value}>
                      {day}
                    </option>
                  ))}
                </select>
              </label>
              <Field
                name={"opens-" + index}
                label="Opens"
                type="time"
                value={window.opens}
                onChange={(event) =>
                  change({
                    hours: settings.hours.map((entry, i) =>
                      i === index
                        ? { ...entry, opens: event.target.value }
                        : entry,
                    ),
                  })
                }
              />
              <Field
                name={"closes-" + index}
                label="Closes (HH:MM)"
                pattern="([01][0-9]|2[0-3]):[0-5][0-9]|24:00"
                placeholder="18:00"
                value={window.closes}
                onChange={(event) =>
                  change({
                    hours: settings.hours.map((entry, i) =>
                      i === index
                        ? { ...entry, closes: event.target.value }
                        : entry,
                    ),
                  })
                }
              />
              <button
                type="button"
                className="icon-button"
                aria-label={"Remove opening window " + (index + 1)}
                onClick={() =>
                  change({
                    hours: settings.hours.filter((_, i) => i !== index),
                  })
                }
              >
                <Icon name="close" />
              </button>
            </div>
          ))}
          <button
            type="button"
            className="button button-outline"
            disabled={settings.hours.length >= 21}
            onClick={() =>
              change({
                hours: [...settings.hours, { day: 0, opens: "", closes: "" }],
              })
            }
          >
            <Icon name="plus" />
            Add opening window
          </button>
        </section>
        <section className="panel form-stack">
          <h3>
            <Icon name="pin" /> Delivery PIN codes
          </h3>
          <p className="small">
            Enter one rule per mode and PIN code. Fees include applicable tax. A
            PIN without a rule cannot check out.
          </p>
          {!settings.rules.length && <p>No delivery areas configured yet.</p>}
          {settings.rules.map((rule, index) => (
            <div className="delivery-rule pin-rule" key={index}>
              <label className="field">
                Shopping mode
                <select
                  value={rule.mode}
                  onChange={(event) =>
                    change({
                      rules: settings.rules.map((entry, i) =>
                        i === index
                          ? {
                              ...entry,
                              mode: event.target.value as "fresh" | "packaged",
                            }
                          : entry,
                      ),
                    })
                  }
                >
                  <option value="packaged">Packaged</option>
                  <option value="fresh">Fresh food</option>
                </select>
              </label>
              <Field
                name={"pin-" + index}
                label="PIN code"
                pattern="[1-9][0-9]{5}"
                maxLength={6}
                inputMode="numeric"
                value={rule.pincode}
                onChange={(event) =>
                  change({
                    rules: settings.rules.map((entry, i) =>
                      i === index
                        ? { ...entry, pincode: event.target.value }
                        : entry,
                    ),
                  })
                }
              />
              <label className="field">
                State
                <select
                  value={rule.state_code}
                  required
                  onChange={(event) =>
                    change({
                      rules: settings.rules.map((entry, i) =>
                        i === index
                          ? { ...entry, state_code: event.target.value }
                          : entry,
                      ),
                    })
                  }
                >
                  <option value="">Select state</option>
                  {Object.entries(STATES)
                    .sort((a, b) => a[1].localeCompare(b[1]))
                    .map(([value, name]) => (
                      <option key={value} value={value}>
                        {name}
                      </option>
                    ))}
                </select>
              </label>
              <Field
                name={"fee-" + index}
                label="Delivery fee (INR)"
                type="number"
                min={0}
                max={100000}
                step="0.01"
                value={rule.fee_paise / 100}
                onChange={(event) =>
                  change({
                    rules: settings.rules.map((entry, i) =>
                      i === index
                        ? {
                            ...entry,
                            fee_paise: Math.round(
                              Number(event.target.value) * 100,
                            ),
                          }
                        : entry,
                    ),
                  })
                }
              />
              <button
                type="button"
                className="icon-button"
                aria-label={"Remove delivery rule " + (index + 1)}
                onClick={() =>
                  change({
                    rules: settings.rules.filter((_, i) => i !== index),
                  })
                }
              >
                <Icon name="close" />
              </button>
            </div>
          ))}
          <button
            type="button"
            className="button button-outline"
            disabled={settings.rules.length >= 1000}
            onClick={() =>
              change({
                rules: [
                  ...settings.rules,
                  {
                    mode: "packaged",
                    pincode: "",
                    state_code: "",
                    fee_paise: 0,
                  },
                ],
              })
            }
          >
            <Icon name="plus" />
            Add PIN code
          </button>
        </section>
        <button className="button">
          {busy ? "Saving delivery settings…" : "Save delivery settings"}
        </button>
      </fieldset>
      <Notice message={message} />
    </form>
  );
}
