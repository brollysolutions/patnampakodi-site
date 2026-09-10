"use client";

import { useState } from "react";
import { api, type Schema } from "@/lib/commerce";
import { Field } from "./FormFields";

type Content = Schema["ContentView"];
const fields: Record<Content["kind"], string[]> = {
  page: ["title", "description", "heading", "intro"],
  brand: ["tagline", "revision", "contact_email", "contact_phone"],
  menu: ["name", "description", "category", "dietary", "price_paise"],
  outlet: [
    "name",
    "city",
    "pincode",
    "address",
    "hours",
    "phone",
    "latitude",
    "longitude",
  ],
  franchise: ["name", "description", "image", "investment_paise"],
};
const choices: Record<string, string[]> = {
  category: ["Dry", "Wet", "Bowls", "Dips", "Drinks"],
  dietary: ["veg", "non-veg", "unconfirmed"],
  image: ["display", "cart", "cabin", "shop"],
};
const numeric = ["price_paise", "investment_paise", "latitude", "longitude"];
const optional = [
  "description",
  "contact_email",
  "contact_phone",
  "address",
  "hours",
  "phone",
  ...numeric,
];
const label = (field: string) =>
  field.replaceAll("_", " ").replace("paise", "in paise (100 = INR 1)");

export function ContentEditor({
  items,
  action,
}: {
  items: Content[];
  action: (operation: () => Promise<unknown>) => Promise<void>;
}) {
  const [selected, setSelected] = useState<Content | null>(null);
  const [kind, setKind] = useState<Content["kind"]>("page");
  const [sectionCount, setSectionCount] = useState(0);
  const sections = (selected?.payload.sections ?? []) as {
    title: string;
    body: string;
  }[];
  return (
    <div className="commerce-grid">
      <section className="panel form-stack">
        <h2>Website content</h2>
        <p>
          Choose an existing item, or add a page, menu item, outlet or franchise
          model. Policy pages use addresses such as policies/shipping.
        </p>
        <button
          className="button button-small"
          onClick={() => {
            setSelected(null);
            setKind("page");
            setSectionCount(0);
          }}
        >
          Add new content
        </button>
        {items.map((item) => (
          <button
            className="button button-small"
            key={item.kind + item.slug}
            onClick={() => {
              setSelected(item);
              setKind(item.kind);
              setSectionCount(
                ((item.payload.sections ?? []) as unknown[]).length,
              );
            }}
          >
            {item.kind}: {item.slug} {item.published ? "" : "(draft)"}
          </button>
        ))}
      </section>
      <form
        className="panel form-stack"
        key={selected?.slug ?? kind}
        onSubmit={(event) => {
          event.preventDefault();
          const data = new FormData(event.currentTarget);
          const slug = String(data.get("slug"));
          const payload: Record<string, unknown> = {};
          for (const key of fields[kind]) {
            const value = String(data.get(key) ?? "");
            payload[key] = numeric.includes(key)
              ? value
                ? Number(value)
                : null
              : optional.includes(key) && !value && key !== "description"
                ? null
                : value;
          }
          if (["page", "menu", "outlet"].includes(kind)) payload.slug = slug;
          if (kind === "menu") payload.featured = data.get("featured") === "on";
          if (kind === "page")
            payload.sections = Array.from({ length: sectionCount }, (_, i) => ({
              title: String(data.get(`title-${i}`)),
              body: String(data.get(`body-${i}`)),
            }));
          void action(() =>
            api("admin/content", {
              method: "PUT",
              body: JSON.stringify({
                kind,
                slug,
                payload,
                position: Number(data.get("position")),
                published: data.get("published") === "on",
              }),
            }),
          );
        }}
      >
        <h2>{selected ? "Edit content" : "Add content"}</h2>
        {!selected && (
          <label className="field">
            Content type
            <select
              value={kind}
              onChange={(e) => {
                setKind(e.target.value as Content["kind"]);
                setSectionCount(0);
              }}
            >
              {Object.keys(fields)
                .filter((key) => key !== "brand")
                .map((key) => (
                  <option key={key}>{key}</option>
                ))}
            </select>
          </label>
        )}
        <Field
          name="slug"
          label="Permanent URL slug or record name"
          defaultValue={selected?.slug}
          readOnly={!!selected}
          pattern="(policies/)?[a-z0-9]+(-[a-z0-9]+)*"
        />
        <Field
          name="position"
          label="Display order"
          type="number"
          min={0}
          max={10000}
          defaultValue={selected?.position ?? 0}
        />
        {fields[kind].map((key) =>
          choices[key] ? (
            <label className="field" key={key}>
              {label(key)}
              <select
                name={key}
                defaultValue={String(selected?.payload[key] ?? choices[key][0])}
              >
                {choices[key].map((value) => (
                  <option key={value}>{value}</option>
                ))}
              </select>
            </label>
          ) : (
            <Field
              key={key}
              name={key}
              label={label(key)}
              type={numeric.includes(key) ? "number" : "text"}
              step="any"
              required={!optional.includes(key)}
              defaultValue={String(selected?.payload[key] ?? "")}
            />
          ),
        )}
        {kind === "menu" && (
          <label className="checkbox">
            <input
              name="featured"
              type="checkbox"
              defaultChecked={Boolean(selected?.payload.featured)}
            />
            Featured on homepage
          </label>
        )}
        {kind === "page" && (
          <>
            <h3>Page sections</h3>
            {Array.from({ length: sectionCount }, (_, i) => (
              <div className="form-stack" key={i}>
                <Field
                  name={`title-${i}`}
                  label={`Section ${i + 1} heading`}
                  defaultValue={sections[i]?.title}
                />
                <label className="field">
                  Section {i + 1} text
                  <textarea
                    name={`body-${i}`}
                    rows={5}
                    required
                    defaultValue={sections[i]?.body}
                  />
                </label>
              </div>
            ))}
            <div className="actions">
              <button
                className="button button-small"
                type="button"
                onClick={() => setSectionCount((value) => value + 1)}
              >
                Add section
              </button>
              {sectionCount > 0 && (
                <button
                  className="button button-small"
                  type="button"
                  onClick={() => setSectionCount((value) => value - 1)}
                >
                  Remove last section
                </button>
              )}
            </div>
          </>
        )}
        <label className="checkbox">
          <input
            name="published"
            type="checkbox"
            defaultChecked={selected?.published}
          />
          Publish approved content
        </label>
        <button className="button">Save content</button>
      </form>
    </div>
  );
}
