"use client";

import { HelpSelect } from "./FieldHelp";
import { useEffect, useState, type FormEvent } from "react";
import Image from "next/image";
import { api, money, type Schema } from "@/lib/commerce";
import { Field, Notice } from "./FormFields";

type Action = (
  operation: () => Promise<unknown>,
  success?: string,
  refresh?: boolean,
) => Promise<void>;

export function LeadDetails({
  item,
  action,
}: {
  item: Schema["EnquiryView"];
  action: Action;
}) {
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const fields = [
      "name",
      "phone",
      "email",
      "city",
      "preferred_model",
      "budget",
      "notes",
    ];
    await action(
      () =>
        api(`admin/enquiries/${item.id}`, {
          method: "PUT",
          body: JSON.stringify(
            Object.fromEntries(
              fields.map((key) => [key, String(form.get(key) ?? "")]),
            ),
          ),
        }),
      "Enquiry details saved.",
    );
  }
  return (
    <details>
      <summary>Edit enquiry details</summary>
      <form className="form-stack" onSubmit={save}>
        <Field
          name="name"
          label="Contact name"
          required={false}
          maxLength={100}
          defaultValue={item.details.name ?? ""}
        />
        <Field
          name="phone"
          label="Contact phone including +91"
          pattern="\+91[6-9][0-9]{9}"
          defaultValue={item.details.phone}
        />
        <Field
          name="email"
          label="Contact email"
          type="email"
          required={false}
          maxLength={254}
          defaultValue={item.details.email ?? ""}
        />
        <Field
          name="city"
          label="Contact city"
          required={false}
          maxLength={100}
          defaultValue={item.details.city ?? ""}
        />
        <Field
          name="preferred_model"
          label="Preferred franchise model"
          required={false}
          maxLength={100}
          defaultValue={item.details.preferred_model ?? ""}
        />
        <Field
          name="budget"
          label="Budget discussed"
          required={false}
          maxLength={100}
          defaultValue={item.details.budget ?? ""}
        />
        <label className="field">
          Staff notes
          <textarea
            name="notes"
            maxLength={4000}
            defaultValue={item.details.notes ?? ""}
          />
        </label>
        <button className="button button-small">Save enquiry details</button>
      </form>
    </details>
  );
}

export function EnquiryExport() {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <section className="panel form-stack">
      <h2>Export enquiries</h2>
      <p>
        Both dates are included, using India time. Exports contain contact
        details.
      </p>
      <form
        className="actions"
        onSubmit={async (event) => {
          event.preventDefault();
          if (busy) return;
          setBusy(true);
          setMessage("");
          const data = new FormData(event.currentTarget);
          const query = new URLSearchParams();
          for (const key of ["start", "end", "status"])
            query.set(key, String(data.get(key) ?? ""));
          try {
            const response = await fetch(
              "/api/v1/admin/enquiries.csv?" + query,
              { cache: "no-store" },
            );
            if (!response.ok) {
              const result = await response.json().catch(() => null);
              throw Error(
                typeof result?.detail === "string"
                  ? result.detail
                  : "Could not export enquiries.",
              );
            }
            const url = URL.createObjectURL(await response.blob());
            const link = document.createElement("a");
            link.href = url;
            link.download = "enquiries.csv";
            document.body.append(link);
            link.click();
            link.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
            setMessage("Enquiry CSV downloaded.");
          } catch (error) {
            setMessage((error as Error).message);
          } finally {
            setBusy(false);
          }
        }}
      >
        <Field name="start" label="Enquiries from date" type="date" />
        <Field name="end" label="Enquiries to date" type="date" />
        <label className="field">
          Enquiry export status
          <select name="status">
            <option value="">All statuses</option>
            {["new", "contacted", "qualified", "won", "lost"].map((status) => (
              <option key={status}>{status}</option>
            ))}
          </select>
        </label>
        <button className="button button-small" disabled={busy}>
          {busy ? "Preparing CSV…" : "Download enquiries CSV"}
        </button>
      </form>
      <Notice message={message} />
    </section>
  );
}

export function SalesReport() {
  const [data, setData] = useState<Schema["SalesSummary"] | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  return (
    <section className="panel form-stack">
      <h2>Sales summary</h2>
      <p>
        Invoices issued in the selected dates, inclusive in India time. Refunds
        are processed refunds to date for those invoices, including refunds
        processed later. Extra or duplicate captures are excluded.
      </p>
      <form
        className="actions"
        onSubmit={async (event) => {
          event.preventDefault();
          if (busy) return;
          setBusy(true);
          setData(null);
          setMessage("Loading sales…");
          const form = new FormData(event.currentTarget);
          try {
            setData(
              await api<Schema["SalesSummary"]>(
                `admin/sales-summary?start=${encodeURIComponent(String(form.get("start")))}&end=${encodeURIComponent(String(form.get("end")))}`,
              ),
            );
            setMessage("Sales summary loaded.");
          } catch (error) {
            setMessage((error as Error).message);
          } finally {
            setBusy(false);
          }
        }}
      >
        <Field name="start" label="Sales from date" type="date" />
        <Field name="end" label="Sales to date" type="date" />
        <button className="button button-small" disabled={busy}>
          Load sales summary
        </button>
      </form>
      <Notice message={message} />
      {data && (
        <>
          <dl className="facts">
            {[
              ["Invoiced orders", data.orders],
              ["Gross sales", money(data.gross_paise)],
              ["Refunded to date", money(data.refunded_paise)],
              ["Net sales", money(data.net_paise)],
            ].map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
          {!data.days.length ? (
            <p>No invoiced sales in this period.</p>
          ) : (
            <div
              className="table-scroll"
              tabIndex={0}
              role="region"
              aria-label="Daily sales"
            >
              <table>
                <caption>
                  Daily invoices from {data.start} to {data.end}
                </caption>
                <thead>
                  <tr>
                    {[
                      "Date (India)",
                      "Orders",
                      "Gross",
                      "Refunded to date",
                      "Net",
                    ].map((value) => (
                      <th key={value} scope="col">
                        {value}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.days.map((day) => (
                    <tr key={day.day}>
                      <th scope="row">{day.day}</th>
                      <td>{day.orders}</td>
                      <td>{money(day.gross_paise)}</td>
                      <td>{money(day.refunded_paise)}</td>
                      <td>{money(day.net_paise)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  );
}

export function MediaSelect({ selected }: { selected: string | null }) {
  const [items, setItems] = useState<Schema["MediaView"][] | null>(null);
  const [value, setValue] = useState(selected ?? "");
  const [message, setMessage] = useState("");
  useEffect(() => {
    let active = true;
    api<Schema["MediaView"][]>("admin/media")
      .then((result) => {
        if (active) setItems(result);
      })
      .catch((error) => {
        if (active) setMessage(error.message);
      });
    return () => {
      active = false;
    };
  }, []);
  return (
    <div className="form-stack">
      <HelpSelect
        label="Product image"
        help="Choose a photograph uploaded in Media. Selecting no uploaded image keeps any existing source image; uploading a photo does not publish the product."
        name="media"
        value={value}
        onChange={(event) => setValue(event.target.value)}
      >
        <option value="">No uploaded image</option>
        {value && !items?.some((item) => item.id === value) && (
          <option value={value}>Current image</option>
        )}
        {items?.map((item) => (
          <option value={item.id} key={item.id}>
            {item.alt}
          </option>
        ))}
      </HelpSelect>
      {!items && !message && <p>Loading media library…</p>}
      {items?.length === 0 && (
        <p>Upload an image in Media to choose it here.</p>
      )}
      <Notice message={message} />
      {value && (
        <Image
          src={`/api/v1/admin/media/${value}`}
          alt={
            items?.find((item) => item.id === value)?.alt ??
            "Current product image"
          }
          width={240}
          height={240}
          unoptimized
          className="product-image"
        />
      )}
    </div>
  );
}
