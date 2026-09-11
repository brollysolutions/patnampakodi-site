"use client";

import { useState } from "react";
import Image from "next/image";
import type { Schema } from "@/lib/commerce";
import { Icon } from "./Icon";

export function CatalogDrafts({
  items,
  onChoose,
}: {
  items: Schema["CatalogDraft"][];
  onChoose: (item: Schema["CatalogDraft"]) => void;
}) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("");
  const [offset, setOffset] = useState(0);
  const filtered = items.filter(
    (item) =>
      (!mode || item.mode === mode) &&
      `${item.name} ${item.category}`
        .toLowerCase()
        .includes(query.trim().toLowerCase()),
  );
  const pageSize = 6;
  return (
    <section
      className="panel form-stack catalog-preparation"
      aria-labelledby="catalog-preparation-title"
    >
      <div>
        <h2 id="catalog-preparation-title">Foods and flavours to set up</h2>
        <p className="small">
          Choose an item from the saved menu to prefill its product form.
          Complete its selling price, food and tax details, then add stock
          before taking orders.
        </p>
      </div>
      {items.length ? (
        <>
          <div className="catalog-draft-filters">
            <label className="field">
              Find a food or flavour
              <input
                type="search"
                value={query}
                maxLength={100}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setOffset(0);
                }}
              />
            </label>
            <label className="field">
              Food range
              <select
                value={mode}
                onChange={(event) => {
                  setMode(event.target.value);
                  setOffset(0);
                }}
              >
                <option value="">All foods and flavours</option>
                <option value="fresh">Fresh food</option>
                <option value="packaged">Ready mixes</option>
              </select>
            </label>
          </div>
          <p className="small" role="status">
            {filtered.length} {filtered.length === 1 ? "item" : "items"}{" "}
            awaiting product details
          </p>
          <ul className="catalog-draft-grid">
            {filtered.slice(offset, offset + pageSize).map((item) => (
              <li key={item.slug} className="catalog-draft">
                {item.image ? (
                  <Image
                    src={item.image}
                    alt=""
                    width={64}
                    height={64}
                    sizes="64px"
                  />
                ) : (
                  <span
                    className="catalog-draft-placeholder"
                    aria-hidden="true"
                  >
                    <Icon name={item.mode === "fresh" ? "fresh" : "box"} />
                  </span>
                )}
                <div>
                  <h3>{item.name}</h3>
                  <p className="small">
                    {item.mode === "fresh" ? "Fresh food" : "Ready mix"}
                  </p>
                  <button
                    className="button button-small button-outline"
                    type="button"
                    aria-label={`Prepare ${item.name}`}
                    onClick={() => onChoose(item)}
                  >
                    Enter details <Icon name="arrow" />
                  </button>
                </div>
              </li>
            ))}
          </ul>
          {!filtered.length && (
            <p>No matching foods. Try another name or food range.</p>
          )}
          {filtered.length > pageSize && (
            <nav
              className="actions admin-pagination"
              aria-label="Food setup pages"
            >
              <button
                type="button"
                className="button button-small"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - pageSize))}
              >
                Previous foods
              </button>
              <span>
                Page {Math.floor(offset / pageSize) + 1} of{" "}
                {Math.ceil(filtered.length / pageSize)}
              </span>
              <button
                type="button"
                className="button button-small"
                disabled={offset + pageSize >= filtered.length}
                onClick={() => setOffset(offset + pageSize)}
              >
                Next foods
              </button>
            </nav>
          )}
        </>
      ) : (
        <p>
          All saved foods have product records. Manage their publication and
          stock below.
        </p>
      )}
    </section>
  );
}
