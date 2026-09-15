"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { api, jsonPost, money, statusLabel, type Schema } from "@/lib/commerce";
import { FulfilmentPanel } from "./FulfilmentPanel";
import { CatalogDrafts } from "./CatalogDrafts";
import { Icon, type IconName } from "./Icon";
import { Field, Notice } from "./FormFields";
import { HelpField, HelpSelect } from "./FieldHelp";
import Image from "next/image";
import {
  EnquiryExport,
  LeadDetails,
  SalesReport,
  MediaSelect,
} from "./AdminExtras";

const tabs = [
  "Orders",
  "Products",
  "Enquiries",
  "Messages",
  "Reports",
  "Delivery",
  "Settings",
  "Media",
] as const;
type Tab = (typeof tabs)[number];
const tabIcons: Record<Tab, IconName> = {
  Orders: "bag",
  Products: "box",
  Enquiries: "users",
  Messages: "mail",
  Reports: "chart",
  Delivery: "truck",
  Settings: "settings",
  Media: "image",
};
const tabDescriptions: Record<Tab, string> = {
  Orders: "Follow every order from payment to delivery.",
  Products: "Manage your catalogue, food information and available stock.",
  Enquiries: "Follow up with people interested in the brand and franchise.",
  Messages:
    "Review delivery updates, provider jobs and items that need attention.",
  Reports: "Review invoiced sales, refunds and exports for your chosen dates.",
  Delivery:
    "Set delivery areas, fees and availability for your fresh-food pilot.",
  Settings:
    "Keep seller details, invoices and operational contacts up to date.",
  Media: "Upload and manage photographs for your product catalogue.",
};
const FOOD_FIELDS = [
  "ingredients",
  "allergens",
  "nutrition",
  "net_quantity",
  "shelf_life",
  "manufacturer",
  "consumer_care",
] as const;
const FOOD_HELP: Record<(typeof FOOD_FIELDS)[number], string> = {
  ingredients:
    "List the confirmed ingredients used in this food or mix, including ingredients in sauces and coatings.",
  allergens:
    "Enter confirmed allergens and any applicable cross-contact information. Do not assume an item is allergen-free.",
  nutrition:
    "Enter the verified nutrition information and its basis, such as per serving or per 100 g.",
  net_quantity:
    "Describe one portion or pack, such as 250 g or 6 pieces. This is not the number available to sell. Use Starting stock when creating a product, or Adjust stock after saving.",
  shelf_life:
    "Enter the confirmed shelf life and storage instructions. Required for packaged products; optional for fresh food.",
  manufacturer:
    "Enter the responsible manufacturer's details for the packaged product. Optional for fresh food.",
  consumer_care:
    "Provide the customer-care contact that should accompany this product, such as an approved phone number or email.",
};
const sentence = (text: string) =>
  text[0].toUpperCase() + text.slice(1).replaceAll("_", " ");

export function AdminPanel() {
  const [session, setSession] = useState<Schema["SessionView"] | null>(null);
  const [checked, setChecked] = useState(false);
  const [tab, setTab] = useState<Tab>("Orders");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    heading.current?.focus({ preventScroll: true });
    heading.current?.scrollIntoView({ block: "start", behavior: "instant" });
  }, [tab]);
  useEffect(() => {
    api<Schema["SessionView"]>("admin/session")
      .then(setSession)
      .catch(() => {})
      .finally(() => setChecked(true));
  }, []);
  async function action(
    operation: () => Promise<unknown>,
    success = "Saved.",
    refresh = true,
  ) {
    setBusy(true);
    setMessage("");
    try {
      await operation();
      setMessage(success);
      if (refresh) setRevision((value) => value + 1);
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const data: Schema["Login"] = {
      username: String(form.get("username") ?? ""),
      password: String(form.get("password") ?? ""),
    };
    await action(
      async () =>
        setSession(
          await api<Schema["SessionView"]>("admin/login", jsonPost(data)),
        ),
      "Signed in.",
    );
  }
  if (!checked) return <Notice message="Checking your session…" />;
  if (!session)
    return (
      <form className="panel form-stack narrow admin-login" onSubmit={login}>
        <span className="admin-login-icon">
          <Icon name="shield" />
        </span>
        <p className="eyebrow">Your store, in one place</p>
        <h2>Admin sign in</h2>
        <p>Manage orders, products and day-to-day operations.</p>
        <Field name="username" label="Username" autoComplete="username" />
        <Field
          name="password"
          label="Password"
          type="password"
          autoComplete="current-password"
          minLength={12}
        />
        <button className="button" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <Notice message={message} />
        <p className="small">
          Your operator supplies account setup. Each person uses their own
          account.
        </p>
      </form>
    );
  return (
    <div className="admin-workspace">
      <aside className="admin-sidebar">
        <p className="admin-nav-label">Workspace</p>
        <nav className="admin-tabs" aria-label="Administration">
          {tabs.map((name) => (
            <button
              key={name}
              className="button button-small"
              aria-current={tab === name ? "page" : undefined}
              aria-controls="admin-content"
              disabled={busy}
              onClick={() => {
                setTab(name);
                setMessage("");
              }}
            >
              <Icon name={tabIcons[name]} />
              {name}
            </button>
          ))}
        </nav>
        <div className="admin-account">
          <span className="admin-avatar" aria-hidden="true">
            {session.username.slice(0, 1).toUpperCase()}
          </span>
          <p>
            <small>Signed in as</small>
            <strong>{session.username}</strong>
          </p>
          <button
            className="admin-signout"
            disabled={busy}
            onClick={() =>
              action(async () => {
                await api("admin/logout", { method: "POST" });
                setSession(null);
              })
            }
          >
            Sign out
          </button>
        </div>
      </aside>
      <div className="admin-content" id="admin-content">
        <div className="admin-section-heading">
          <div>
            <p className="eyebrow">Store management</p>
            <h2 ref={heading} tabIndex={-1}>
              {tab}
            </h2>
            <p>{tabDescriptions[tab]}</p>
          </div>
          <button
            type="button"
            className="button button-small button-outline"
            disabled={busy}
            onClick={() => {
              setMessage("");
              setRevision((value) => value + 1);
            }}
          >
            <Icon name="refresh" /> Refresh
          </button>
        </div>
        <Notice message={message} />
        <fieldset
          className="admin-fields"
          key={`${tab}-${revision}`}
          aria-busy={busy}
          disabled={busy}
        >
          <legend className="sr-only">{tab}</legend>
          {tab === "Orders" && <Orders action={action} />}
          {tab === "Products" && <Products action={action} />}
          {tab === "Enquiries" && <Enquiries action={action} />}
          {tab === "Messages" && <Messages action={action} />}
          {tab === "Reports" && <Reports />}
          {tab === "Delivery" && <FulfilmentPanel />}
          {tab === "Settings" && <Settings action={action} />}
          {tab === "Media" && <Media action={action} />}
        </fieldset>
      </div>
    </div>
  );
}
type Action = (
  operation: () => Promise<unknown>,
  success?: string,
  refresh?: boolean,
) => Promise<void>;
function useLoad<T>(path: string, revision = 0) {
  const [result, setResult] = useState<{
    path: string;
    revision: number;
    data: T;
  } | null>(null);
  const [failure, setFailure] = useState({ path: "", revision: 0, error: "" });
  useEffect(() => {
    let active = true;
    api<T>(path)
      .then((result) => {
        if (active) setResult({ path, revision, data: result });
      })
      .catch((err) => {
        if (active) setFailure({ path, revision, error: err.message });
      });
    return () => {
      active = false;
    };
  }, [path, revision]);
  return {
    data:
      result?.path === path && result.revision === revision
        ? result.data
        : null,
    error:
      failure.path === path && failure.revision === revision
        ? failure.error
        : "",
  };
}
function Pagination({
  offset,
  count,
  size = 100,
  onPage,
}: {
  offset: number;
  count: number;
  size?: number;
  onPage: (offset: number) => void;
}) {
  return (
    <nav className="actions admin-pagination" aria-label="Results pages">
      <button
        className="button button-small"
        type="button"
        disabled={offset === 0}
        onClick={() => onPage(Math.max(0, offset - size))}
      >
        Previous page
      </button>
      <span>Page {Math.floor(offset / size) + 1}</span>
      <button
        className="button button-small"
        type="button"
        disabled={count < size}
        onClick={() => onPage(offset + size)}
      >
        Next page
      </button>
    </nav>
  );
}
function Load({ error }: { error: string }) {
  return <Notice message={error || "Loading…"} />;
}

function Orders({ action }: { action: Action }) {
  const [search, setSearch] = useState("");
  const [offset, setOffset] = useState(0);
  const { data, error } = useLoad<Schema["OrderView"][]>(
    "admin/orders?search=" + encodeURIComponent(search) + "&offset=" + offset,
  );
  const [link, setLink] = useState("");
  return (
    <>
      <form
        className="panel admin-order-search"
        onSubmit={(event) => {
          event.preventDefault();
          setOffset(0);
          setSearch(
            String(new FormData(event.currentTarget).get("search") ?? ""),
          );
        }}
      >
        <Field name="search" label="Order number or phone" required={false} />
        <button className="button button-small">
          <Icon name="search" /> Search orders
        </button>
      </form>
      {data && data.length > 0 && (
        <section
          className="admin-order-overview"
          aria-label="Order summary for this page"
        >
          <p className="small">
            In this view · {data.length}{" "}
            {data.length === 1 ? "order" : "orders"}
            {search ? " matching your search" : ""}
          </p>
          <dl className="admin-metrics">
            {[
              ["Payment confirmed", "paid", "check"],
              ["Preparing", "preparing", "fresh"],
              ["Dispatched", "dispatched", "truck"],
              ["Delivery issues", "delivery_issue", "pin"],
            ].map(([label, status, icon]) => (
              <div key={status}>
                <dt>
                  <Icon name={icon as IconName} />
                  {label}
                </dt>
                <dd>
                  {data.filter((order) => order.status === status).length}
                </dd>
              </div>
            ))}
          </dl>
        </section>
      )}
      <Pagination
        offset={offset}
        count={data?.length ?? 0}
        onPage={setOffset}
      />
      {link && (
        <div className="notice">
          <p>
            Share only after verifying the customer’s identity. Previous links
            are revoked.
          </p>
          <a href={link}>Recovered private order link</a>
        </div>
      )}
      {!data ? (
        <Load error={error} />
      ) : !data.length ? (
        <div className="panel admin-empty">
          <Icon name={search ? "search" : "bag"} />
          <h3>
            {search ? "No matching orders" : "Your orders will appear here"}
          </h3>
          <p>
            {search
              ? "Try another order number or phone number."
              : "When a customer places an order, you can follow its progress and manage delivery here."}
          </p>
        </div>
      ) : (
        data.map((order) => (
          <article className="panel order-admin" key={order.id}>
            <div className="order-admin-heading">
              <div>
                <span className="order-mode">
                  <Icon
                    name={order.shopping_mode === "fresh" ? "fresh" : "box"}
                  />
                  {order.shopping_mode === "fresh" ? "Fresh food" : "Packaged"}
                </span>
                <h3>{order.reference}</h3>
              </div>
              <span className="order-status" data-status={order.status}>
                {statusLabel(order.status)}
              </span>
            </div>
            <div className="order-admin-customer">
              <p>
                <Icon name="users" />
                <span>
                  <strong>{order.customer.name}</strong>
                  <br />
                  {order.customer.phone}
                </span>
              </p>
              <p>
                <Icon name="pin" />
                <span>
                  {order.customer.address}, {order.customer.city},{" "}
                  {order.customer.pincode}
                </span>
              </p>
            </div>
            <ul className="order-admin-lines">
              {order.lines.map((line) => (
                <li key={line.variant_id}>
                  {line.quantity} × {line.name} —{" "}
                  {money(line.quantity * line.price_paise)}
                </li>
              ))}
            </ul>
            <p className="order-admin-total">
              <span>Order total</span>
              <strong>
                {order.total_paise
                  ? money(order.total_paise)
                  : "Awaiting quotation"}
              </strong>
            </p>
            {order.checkout_kind === "staff" &&
              ["requested", "approved"].includes(order.status) && (
                <form
                  className="actions"
                  onSubmit={(event) => {
                    event.preventDefault();
                    const fee = Number(
                      new FormData(event.currentTarget).get("fee"),
                    );
                    void action(() =>
                      api(
                        `admin/orders/${order.id}/approve`,
                        jsonPost({ delivery_paise: Math.round(fee * 100) }),
                      ),
                    );
                  }}
                >
                  <Field
                    name="fee"
                    label="Delivery fee (INR, including tax)"
                    type="number"
                    min={0}
                    step="0.01"
                    defaultValue={order.delivery_paise / 100}
                  />
                  <button className="button">Confirm delivery & quote</button>
                </form>
              )}
            <div className="actions">
              {order.status === "paid" && order.shopping_mode === "fresh" && (
                <button
                  className="button button-small"
                  onClick={() =>
                    action(() =>
                      api(
                        `admin/orders/${order.id}/status`,
                        jsonPost({ status: "preparing" }),
                      ),
                    )
                  }
                >
                  Start preparing
                </button>
              )}
              {((order.status === "paid" && order.shopping_mode !== "fresh") ||
                order.status === "preparing") && (
                <button
                  className="button button-small"
                  onClick={() =>
                    action(() =>
                      api(
                        `admin/orders/${order.id}/status`,
                        jsonPost({ status: "dispatched" }),
                      ),
                    )
                  }
                >
                  Mark dispatched
                </button>
              )}
              {["dispatched", "delivery_issue"].includes(order.status) && (
                <button
                  className="button button-small"
                  onClick={() =>
                    action(() =>
                      api(
                        `admin/orders/${order.id}/status`,
                        jsonPost({ status: "delivered" }),
                      ),
                    )
                  }
                >
                  Mark delivered
                </button>
              )}
              {order.status === "dispatched" && (
                <button
                  className="button button-small"
                  onClick={() =>
                    action(() =>
                      api(
                        `admin/orders/${order.id}/status`,
                        jsonPost({ status: "delivery_issue" }),
                      ),
                    )
                  }
                >
                  Mark delivery issue
                </button>
              )}
              {order.invoice_number && (
                <a
                  className="button button-small button-outline"
                  href={`/api/v1/admin/orders/${order.id}/invoice`}
                  target="_blank"
                  rel="noreferrer"
                >
                  <Icon name="document" />
                  Print / download invoice
                </a>
              )}
            </div>
            <details>
              <summary>Cancellation, refund, and link recovery</summary>
              <div className="form-stack">
                {order.checkout_kind === "staff" &&
                  ["requested", "approved"].includes(order.status) && (
                    <button
                      className="button button-small"
                      onClick={() =>
                        action(() =>
                          api(
                            `admin/orders/${order.id}/status`,
                            jsonPost({ status: "declined" }),
                          ),
                        )
                      }
                    >
                      Decline delivery request
                    </button>
                  )}
                {[
                  "requested",
                  "approved",
                  "payment_pending",
                  "paid",
                  "preparing",
                ].includes(order.status) && (
                  <button
                    className="button button-small"
                    onClick={() =>
                      action(() =>
                        api(`admin/orders/${order.id}/cancel`, {
                          method: "POST",
                        }),
                      )
                    }
                  >
                    {order.status === "preparing"
                      ? "Stop preparation and refund captured payment"
                      : "Cancel order and refund captured payment"}
                  </button>
                )}
                {order.status === "preparing" && (
                  <p className="small">
                    Confirm with the kitchen before cancelling. Prepared food is
                    not automatically returned to stock.
                  </p>
                )}
                {order.invoice_number && (
                  <form
                    className="form-stack"
                    onSubmit={(event) => {
                      event.preventDefault();
                      const form = new FormData(event.currentTarget);
                      void action(
                        () =>
                          api(
                            `admin/orders/${order.id}/refund`,
                            jsonPost({
                              amount: Math.round(
                                Number(form.get("amount")) * 100,
                              ),
                              reason: String(form.get("reason")),
                            }),
                          ),
                        "Refund requested; confirmation is pending.",
                      );
                    }}
                  >
                    <Field
                      name="amount"
                      label="Refund amount in INR"
                      type="number"
                      min="0.01"
                      step="0.01"
                    />
                    <Field
                      name="reason"
                      label="Refund reason"
                      minLength={3}
                      maxLength={200}
                    />
                    <button className="button button-small">
                      Request refund
                    </button>
                  </form>
                )}
                <button
                  className="button button-small"
                  onClick={() =>
                    action(
                      async () => {
                        const result = await api<Schema["RequestReceipt"]>(
                          `admin/orders/${order.id}/recover-link`,
                          { method: "POST" },
                        );
                        setLink(
                          window.location.origin +
                            "/track/#access=" +
                            result.access_token,
                        );
                      },
                      "New link issued. Verify identity before sharing.",
                      false,
                    )
                  }
                >
                  Replace private link after identity verification
                </button>
              </div>
            </details>
          </article>
        ))
      )}
    </>
  );
}

function Products({ action }: { action: Action }) {
  const emptyFilters = { q: "", mode: "", status: "", offset: 0 };
  const [filters, setFilters] = useState(emptyFilters);
  const [revision, setRevision] = useState(0);
  const params = new URLSearchParams({
    ...filters,
    offset: String(filters.offset),
    limit: "20",
  });
  const { data, error } = useLoad<Schema["ProductPage"]>(
    `admin/products?${params}`,
    revision,
  );
  const { data: drafts, error: draftError } = useLoad<Schema["CatalogDraft"][]>(
    "admin/catalog-drafts",
    revision,
  );
  const [editing, setEditing] = useState<Schema["VariantView"] | null>(null);
  const [draft, setDraft] = useState<Schema["CatalogDraft"] | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [editorVersion, setEditorVersion] = useState(0);
  const [deleting, setDeleting] = useState<string | null>(null);
  const listHeading = useRef<HTMLHeadingElement>(null);
  const editorHeading = useRef<HTMLHeadingElement>(null);
  const [mode, setMode] = useState<"fresh" | "packaged">("packaged");
  const { data: storefront } = useLoad<Schema["Storefront"]>("storefront");
  const selectedMode = editing?.product.mode ?? draft?.mode ?? mode;
  useEffect(() => {
    if (editorOpen) {
      editorHeading.current?.focus({ preventScroll: true });
      editorHeading.current?.scrollIntoView({
        block: "start",
        behavior: "instant",
      });
    }
  }, [editing, draft, editorOpen, editorVersion]);
  function addNew() {
    setDraft(null);
    setEditing(null);
    setEditorVersion((value) => value + 1);
    setEditorOpen(true);
  }
  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload: Schema["VariantInput"] = {
      sku: String(form.get("sku")),
      product: {
        ...editing?.product,
        slug: String(form.get("slug")),
        name: String(form.get("name")),
        description: String(form.get("description")),
        dietary: String(form.get("dietary")) as "veg" | "non-veg",
        ingredients: String(form.get("ingredients")),
        allergens: String(form.get("allergens")),
        nutrition: String(form.get("nutrition")),
        net_quantity: String(form.get("net_quantity")),
        shelf_life: String(form.get("shelf_life")),
        manufacturer: String(form.get("manufacturer")),
        consumer_care: String(form.get("consumer_care")),
        image: editing?.product.image ?? draft?.image ?? "",
        mode: selectedMode,
        outlet_slug:
          selectedMode === "fresh" ? String(form.get("outlet_slug") ?? "") : "",
        category: String(form.get("category") ?? "").trim(),
        tags: String(form.get("tags") ?? "")
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
        compare_at_price_paise: form.get("compare")
          ? Math.round(Number(form.get("compare")) * 100)
          : null,
        price_paise: Math.round(Number(form.get("price")) * 100),
      },
      gst_bps: Math.round(Number(form.get("gst")) * 100),
      hsn: String(form.get("hsn")),
      published: form.get("published") === "on",
      media_id: String(form.get("media") ?? "") || null,
    };
    await action(
      async () => {
        const body = editing
          ? payload
          : ({
              ...payload,
              initial_stock: Number(form.get("initial_stock")),
            } satisfies Schema["VariantCreate"]);
        const saved = await api<Schema["VariantView"]>(
          editing ? `admin/variants/${editing.id}` : "admin/variants",
          {
            method: editing ? "PUT" : "POST",
            body: JSON.stringify(body),
          },
        );
        setEditing(saved);
        setDraft(null);
        setFilters({ ...emptyFilters, q: saved.sku });
        setRevision((value) => value + 1);
      },
      "Product saved. It is shown in the saved catalogue.",
      false,
    );
  }
  return (
    <>
      <div className="commerce-grid">
        <section
          className="panel form-stack"
          aria-labelledby="saved-products-title"
        >
          <h2 id="saved-products-title" ref={listHeading} tabIndex={-1}>
            Saved products
          </h2>
          <p className="small">
            Your created products, including drafts and items with no stock.
          </p>
          <button
            type="button"
            className="button button-small"
            onClick={addNew}
          >
            Add product
          </button>
          <form
            className="form-stack"
            key={`${filters.q}-${filters.mode}-${filters.status}`}
            onSubmit={(event) => {
              event.preventDefault();
              const form = new FormData(event.currentTarget);
              setFilters({
                q: String(form.get("q") ?? "").trim(),
                mode: String(form.get("mode") ?? ""),
                status: String(form.get("status") ?? ""),
                offset: 0,
              });
            }}
          >
            <Field
              name="q"
              label="Search saved products"
              type="search"
              required={false}
              maxLength={100}
              defaultValue={filters.q}
              placeholder="Product name or SKU"
            />
            <div className="catalog-draft-filters">
              <label className="field">
                Product range
                <select name="mode" defaultValue={filters.mode}>
                  <option value="">All ranges</option>
                  <option value="fresh">Fresh food</option>
                  <option value="packaged">Packaged</option>
                </select>
              </label>
              <label className="field">
                Publication status
                <select name="status" defaultValue={filters.status}>
                  <option value="">All statuses</option>
                  <option value="published">Published</option>
                  <option value="draft">Draft</option>
                </select>
              </label>
            </div>
            <div className="actions">
              <button className="button button-small">Apply filters</button>
              <button
                type="button"
                className="button button-small button-outline"
                onClick={() => setFilters(emptyFilters)}
              >
                Clear filters
              </button>
            </div>
          </form>
          <details>
            <summary>Import or export products CSV</summary>
            <a href="/api/v1/admin/products.csv">Export products CSV</a>
            <form
              className="form-stack"
              onSubmit={(event) => {
                event.preventDefault();
                const file = new FormData(event.currentTarget).get(
                  "csv",
                ) as File;
                void action(() =>
                  api("admin/products.csv", {
                    method: "POST",
                    body: file,
                    headers: { "Content-Type": "text/csv" },
                  }),
                );
              }}
            >
              <Field
                name="csv"
                label="Import product CSV"
                type="file"
                accept=".csv,text/csv"
              />
              <button className="button button-small">Import all rows</button>
            </form>
          </details>
          {!data ? (
            <Load error={error} />
          ) : (
            <>
              <p className="small" role="status">
                {data.total} {data.total === 1 ? "product" : "products"}
                {filters.q || filters.mode || filters.status
                  ? " matching your filters"
                  : " saved"}
              </p>
              {!data.total && (
                <p>
                  {filters.q || filters.mode || filters.status
                    ? "No matching products. Clear the filters or search another name or SKU."
                    : "No products saved yet. Add a product or choose a food from the menu suggestions."}
                </p>
              )}
              {data.items.map((item) => (
                <article key={item.id} className="stock-row">
                  <h3>{item.product.name}</h3>
                  <p>
                    {item.sku} ·{" "}
                    {item.product.mode === "fresh" ? "Fresh" : "Packaged"} ·{" "}
                    {item.published ? "Published" : "Draft"}
                    <br />
                    Stock {item.stock} · Reserved {item.reserved}
                    <br />
                    {money(item.product.price_paise)} ·{" "}
                    {item.product.net_quantity}
                  </p>
                  {item.stock - item.reserved === 0 && (
                    <p className="small">No stock available for new orders.</p>
                  )}
                  <details>
                    <summary>View details</summary>
                    <p>{item.product.description}</p>
                    <dl className="facts">
                      {FOOD_FIELDS.map((key) => (
                        <div key={key}>
                          <dt>{sentence(key)}</dt>
                          <dd>{item.product[key] || "Not supplied"}</dd>
                        </div>
                      ))}
                      <div>
                        <dt>HSN / GST</dt>
                        <dd>
                          {item.hsn} / {item.gst_bps / 100}%
                        </dd>
                      </div>
                    </dl>
                  </details>
                  <div className="actions">
                    <button
                      className="button button-small"
                      onClick={() => {
                        setDraft(null);
                        setEditing(item);
                        setEditorOpen(true);
                      }}
                    >
                      Edit product
                    </button>
                    <button
                      type="button"
                      className="button button-small button-outline"
                      onClick={() =>
                        void action(
                          async () => {
                            const { sku, product, gst_bps, hsn, media_id } =
                              item;
                            await api(`admin/variants/${item.id}`, {
                              method: "PUT",
                              body: JSON.stringify({
                                sku,
                                product,
                                gst_bps,
                                hsn,
                                media_id,
                                published: !item.published,
                              } satisfies Schema["VariantInput"]),
                            });
                            if (editing?.id === item.id)
                              setEditing({
                                ...item,
                                published: !item.published,
                              });
                            setRevision((value) => value + 1);
                          },
                          item.published
                            ? "Product unpublished."
                            : "Product published.",
                          false,
                        )
                      }
                    >
                      {item.published ? "Unpublish" : "Publish"}
                    </button>
                    <button
                      type="button"
                      className="button button-small button-outline"
                      data-delete-trigger
                      disabled={item.reserved > 0}
                      onClick={() => setDeleting(item.id)}
                    >
                      Delete product
                    </button>
                  </div>
                  {deleting === item.id && (
                    <div className="delete-product-confirmation" role="alert">
                      <p>
                        Delete {item.product.name}? This permanently removes the
                        product and its stock. Products with order history
                        cannot be deleted.
                      </p>
                      <div className="actions">
                        <button
                          type="button"
                          className="button button-small"
                          onClick={() =>
                            void action(
                              async () => {
                                await api(`admin/variants/${item.id}`, {
                                  method: "DELETE",
                                });
                                setDeleting(null);
                                if (editing?.id === item.id) {
                                  setEditing(null);
                                  setEditorOpen(false);
                                }
                                setFilters({ ...filters, offset: 0 });
                                setRevision((value) => value + 1);
                                listHeading.current?.focus();
                              },
                              "Product deleted.",
                              false,
                            )
                          }
                        >
                          Confirm delete
                        </button>
                        <button
                          type="button"
                          className="button button-small button-outline"
                          onClick={(event) => {
                            event.currentTarget
                              .closest("article")
                              ?.querySelector<HTMLButtonElement>(
                                "[data-delete-trigger]",
                              )
                              ?.focus();
                            setDeleting(null);
                          }}
                        >
                          Cancel deletion
                        </button>
                      </div>
                    </div>
                  )}
                  <details>
                    <summary>Adjust stock</summary>
                    <form
                      className="actions"
                      onSubmit={(event) => {
                        event.preventDefault();
                        const form = new FormData(event.currentTarget);
                        void action(
                          async () => {
                            await api(
                              `admin/variants/${item.id}/stock`,
                              jsonPost({
                                delta: Number(form.get("delta")),
                                reason: String(form.get("reason")),
                              }),
                            );
                            setRevision((value) => value + 1);
                          },
                          "Stock updated.",
                          false,
                        );
                      }}
                    >
                      <Field
                        name="delta"
                        label={`Stock adjustment for ${item.sku}`}
                        type="number"
                        step={1}
                      />
                      <Field
                        name="reason"
                        label="Adjustment reason"
                        minLength={3}
                      />
                      <button className="button button-small">
                        Adjust stock
                      </button>
                    </form>
                  </details>
                </article>
              ))}
              {data.total > 20 && (
                <nav
                  className="actions admin-pagination"
                  aria-label="Saved product pages"
                >
                  <button
                    type="button"
                    className="button button-small"
                    disabled={filters.offset === 0}
                    onClick={() =>
                      setFilters({
                        ...filters,
                        offset: Math.max(0, filters.offset - 20),
                      })
                    }
                  >
                    Previous products
                  </button>
                  <span>
                    Page {Math.floor(filters.offset / 20) + 1} of{" "}
                    {Math.ceil(data.total / 20)}
                  </span>
                  <button
                    type="button"
                    className="button button-small"
                    disabled={filters.offset + 20 >= data.total}
                    onClick={() =>
                      setFilters({ ...filters, offset: filters.offset + 20 })
                    }
                  >
                    Next products
                  </button>
                </nav>
              )}
            </>
          )}
        </section>
        <div className="form-stack">
          <details className="panel">
            <summary>Choose a food from the menu</summary>
            {drafts ? (
              <CatalogDrafts
                items={drafts}
                onChoose={(item) => {
                  setEditing(null);
                  setDraft(item);
                  setEditorOpen(true);
                }}
              />
            ) : (
              <Load error={draftError} />
            )}
          </details>
          {!editorOpen && (
            <p className="small">
              Select Edit product to update a saved item, or Add product to
              create one.
            </p>
          )}
          {editorOpen && (
            <form
              className="panel form-stack"
              onSubmit={save}
              key={editing?.id ?? draft?.slug ?? `new-${editorVersion}`}
            >
              <h2 ref={editorHeading} tabIndex={-1}>
                {editing
                  ? "Edit product"
                  : draft
                    ? `Set up ${draft.name}`
                    : "Add product"}
              </h2>
              <button
                type="button"
                className="button button-small button-outline"
                onClick={() => {
                  setEditorOpen(false);
                  listHeading.current?.focus();
                  listHeading.current?.scrollIntoView({
                    block: "start",
                    behavior: "instant",
                  });
                }}
              >
                Back to saved products
              </button>
              {draft && (
                <p className="small">
                  The name, category and available artwork are prefilled.
                  Confirm the remaining food, price and tax information before
                  publishing.
                </p>
              )}
              <HelpSelect
                label="Shopping mode"
                help="Choose fresh food prepared by an outlet or a packaged product. This choice is permanent after the product is created."
                value={selectedMode}
                disabled={Boolean(editing || draft)}
                onChange={(event) =>
                  setMode(event.target.value as "fresh" | "packaged")
                }
              >
                <option value="packaged">Packaged product</option>
                <option value="fresh">Fresh food</option>
              </HelpSelect>
              {selectedMode === "fresh" && (
                <>
                  <HelpSelect
                    label="Preparation outlet"
                    help="Choose the published outlet that prepares this fresh item. The outlet cannot change after saving. Configure ordering hours and coverage in Delivery."
                    name="outlet_slug"
                    required
                    defaultValue={editing?.product.outlet_slug ?? ""}
                    disabled={Boolean(editing)}
                  >
                    <option value="">Choose a published outlet</option>
                    {storefront?.outlets.map((outlet) => (
                      <option key={outlet.slug} value={outlet.slug}>
                        {outlet.name}
                      </option>
                    ))}
                  </HelpSelect>
                  {editing && (
                    <input
                      type="hidden"
                      name="outlet_slug"
                      value={editing.product.outlet_slug}
                    />
                  )}
                </>
              )}
              {editing && (
                <p className="small">
                  Mode and preparation outlet are permanent. Create a new
                  product to change them.
                </p>
              )}
              {(editing || draft) && (
                <button
                  type="button"
                  className="button button-small"
                  onClick={addNew}
                >
                  Add another product
                </button>
              )}
              <HelpField
                name="sku"
                label="SKU"
                help="A unique internal product code, up to 64 letters, numbers, underscores or hyphens. Use it to identify this item in stock and CSV files."
                defaultValue={editing?.sku ?? draft?.sku}
                pattern={"[A-Za-z0-9_\\-]{1,64}"}
              />
              <HelpField
                name="slug"
                label="Permanent product URL slug"
                help="The product's permanent URL name. Use lowercase words separated by hyphens. It cannot be changed after creation."
                defaultValue={editing?.product.slug ?? draft?.slug}
                readOnly={Boolean(editing || draft)}
                pattern="[a-z0-9]+(-[a-z0-9]+)*"
              />
              <HelpField
                name="name"
                label="Product name"
                help="The name customers and staff will see. Include the flavour or product type so this item is easy to recognize."
                defaultValue={editing?.product.name ?? draft?.name}
              />
              <HelpField
                name="description"
                label="Description"
                help="Describe the food, flavour and what the customer receives. Use confirmed details rather than unverified claims."
                defaultValue={
                  editing?.product.description ?? draft?.description
                }
              />
              <HelpField
                name="price"
                label="Price in INR including tax"
                help="Enter the price for one sellable portion or pack in rupees, including applicable tax. Stock is managed separately."
                type="number"
                min="0.01"
                step="0.01"
                defaultValue={
                  editing ? editing.product.price_paise / 100 : undefined
                }
              />
              <HelpField
                name="category"
                label="Category URL slug (optional)"
                help="An optional grouping for shop filters. Use lowercase words separated by hyphens, such as ready-mixes."
                required={false}
                defaultValue={
                  editing?.product.category ?? draft?.category ?? ""
                }
                pattern="[a-z0-9]+(-[a-z0-9]+)*"
                maxLength={80}
              />
              {!editing && (
                <HelpField
                  name="initial_stock"
                  label="Starting stock"
                  help="How many portions or packs are available to sell? For example, enter 5 for five bowls. Enter 0 to keep the item unavailable. After saving, use Adjust stock in the saved product list."
                  type="number"
                  min={0}
                  max={1000000}
                  step={1}
                  defaultValue={0}
                />
              )}
              <HelpField
                name="tags"
                label="Tag URL slugs, comma separated (optional)"
                help="Optional search and discovery tags, separated by commas. Each tag uses lowercase words joined with hyphens."
                required={false}
                defaultValue={
                  (editing?.product.tags ?? draft?.tags)?.join(", ") ?? ""
                }
              />
              <HelpField
                name="compare"
                label="Original price in INR (optional)"
                help="Only enter a genuine original price higher than the current selling price. Leave blank when no original-price comparison applies."
                type="number"
                required={false}
                min="0.01"
                step="0.01"
                defaultValue={
                  editing?.product.compare_at_price_paise
                    ? editing.product.compare_at_price_paise / 100
                    : ""
                }
              />
              <HelpSelect
                label="Dietary mark"
                help="Choose Vegetarian or Non-vegetarian using the product's confirmed ingredients. Review this value for every food."
                name="dietary"
                required
                defaultValue={
                  editing?.product.dietary ??
                  (draft?.dietary === "unconfirmed" ? "" : draft?.dietary) ??
                  "non-veg"
                }
              >
                <option value="">Confirm dietary mark</option>
                <option value="veg">Vegetarian</option>
                <option value="non-veg">Non-vegetarian</option>
              </HelpSelect>
              {FOOD_FIELDS.map((key) => (
                <HelpField
                  key={key}
                  name={key}
                  label={
                    key === "net_quantity"
                      ? "Portion or pack size"
                      : sentence(key)
                  }
                  help={FOOD_HELP[key]}
                  required={
                    selectedMode === "packaged" ||
                    !["shelf_life", "manufacturer"].includes(key)
                  }
                  defaultValue={editing?.product[key]}
                />
              ))}
              <HelpField
                name="gst"
                label="GST rate (%)"
                help="Enter the confirmed GST percentage for this product. Use the rate approved for your product classification; the selling price above already includes tax."
                type="number"
                min={0}
                max={40}
                step="0.01"
                defaultValue={editing ? editing.gst_bps / 100 : undefined}
              />
              <HelpField
                name="hsn"
                label="HSN code"
                help="Enter the confirmed 4–8 digit HSN classification used for this product's invoices. Check it against your approved tax records."
                pattern="[0-9]{4,8}"
                defaultValue={editing?.hsn}
              />
              <MediaSelect selected={editing?.media_id ?? null} />
              <HelpField
                key={`${editing?.id ?? "new"}-${editing?.published ?? false}`}
                label="Publish after verifying all food and tax information"
                help="Published products can appear in the storefront. Taking orders also requires available stock and valid delivery settings. Leave unchecked to save a draft."
                type="checkbox"
                name="published"
                required={false}
                defaultChecked={editing?.published}
              />
              <button className="button">Save product</button>
            </form>
          )}
        </div>
      </div>
    </>
  );
}

function Enquiries({ action }: { action: Action }) {
  const [offset, setOffset] = useState(0);
  const { data, error } = useLoad<Schema["EnquiryView"][]>(
    "admin/enquiries?offset=" + offset,
  );
  return (
    <>
      <EnquiryExport />
      <Pagination
        offset={offset}
        count={data?.length ?? 0}
        onPage={setOffset}
      />
      {!data ? (
        <Load error={error} />
      ) : !data.length ? (
        <p>No franchise enquiries yet.</p>
      ) : (
        <div className="product-grid">
          {data.map((item) => (
            <article className="panel form-stack" key={item.id}>
              <h2>{item.details.name || item.details.phone}</h2>
              <p>
                {item.details.phone}
                <br />
                {item.details.email}
                <br />
                {item.details.city}
              </p>
              {item.details.purpose && (
                <p>Interest: {sentence(item.details.purpose)}</p>
              )}
              {(item.details.preferred_model || item.details.budget) && (
                <p>
                  {[item.details.preferred_model, item.details.budget]
                    .filter(Boolean)
                    .join(" · ")}
                </p>
              )}
              <p>
                Source:{" "}
                {[item.attribution.source, item.attribution.campaign]
                  .filter(Boolean)
                  .join(" · ")}
              </p>
              <LeadDetails item={item} action={action} />
              <form
                className="form-stack"
                onSubmit={(event) => {
                  event.preventDefault();
                  void action(() =>
                    api(
                      `admin/enquiries/${item.id}/status`,
                      jsonPost({
                        status: new FormData(event.currentTarget).get("status"),
                      }),
                    ),
                  );
                }}
              >
                <label className="field">
                  Pipeline status
                  <select name="status" defaultValue={item.status}>
                    {["new", "contacted", "qualified", "won", "lost"].map(
                      (status) => (
                        <option key={status}>{status}</option>
                      ),
                    )}
                  </select>
                </label>
                <button className="button button-small">Update status</button>
              </form>
            </article>
          ))}
        </div>
      )}
    </>
  );
}
function Messages({ action }: { action: Action }) {
  const [offset, setOffset] = useState(0);
  const { data, error } = useLoad<Schema["OutboxView"][]>(
    "admin/messages?offset=" + offset,
  );
  const health = useLoad<Schema["OperationsView"]>("admin/operations");
  return !data ? (
    <Load error={error} />
  ) : (
    <div className="form-stack">
      <section className="panel form-stack">
        <h2>Operations health</h2>
        {!health.data ? (
          <Load error={health.error} />
        ) : (
          <>
            {!health.data.checks.length && (
              <p>
                No worker heartbeat yet. Ask the operator to start the
                scheduler.
              </p>
            )}
            {health.data.checks.map((check) => (
              <p key={check.name}>
                {sentence(check.name)}: {check.status}
                {check.overdue
                  ? " — overdue, operator attention required"
                  : ""}{" "}
                · {new Date(check.checked_at).toLocaleString("en-IN")}
              </p>
            ))}
            <details>
              <summary>
                Settlement comparison (
                {health.data.settlements.filter((item) => !item.matches).length}{" "}
                to review)
              </summary>
              <p>
                Current and previous month. Verify unmatched transactions
                against the Razorpay report.
              </p>
              {health.data.settlements.map((item) => (
                <p key={item.id}>
                  {item.id} · {item.kind} · {money(item.amount)} ·{" "}
                  {item.matches ? "Matches ledger" : "Review required"}
                </p>
              ))}
            </details>
          </>
        )}
      </section>
      <p>Check this queue during operations. WhatsApp has no email fallback.</p>
      <Pagination
        offset={offset}
        count={data.length}
        size={200}
        onPage={setOffset}
      />
      {!data.length && <p>No queued messages or provider jobs.</p>}
      {data.map((item) => (
        <article className="panel" key={item.id}>
          <h3>{sentence(item.kind)}</h3>
          <p>
            {item.status} · {item.attempts} attempts
            {item.overdue ? " · Delivery overdue" : ""}
          </p>
          <p>{item.last_error}</p>
          {item.status === "failed" && (
            <button
              className="button button-small"
              onClick={() =>
                action(() =>
                  api(`admin/messages/${item.id}/retry`, { method: "POST" }),
                )
              }
            >
              Retry failed job
            </button>
          )}
        </article>
      ))}
    </div>
  );
}
function Settings({ action }: { action: Action }) {
  const { data, error } =
    useLoad<Schema["BusinessSettings-Output"]>("admin/settings");
  if (error) return <Load error={error} />;
  return (
    <form
      className="panel form-stack narrow"
      key={data?.gstin ?? "new"}
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const payload = {
          ...Object.fromEntries(
            [
              "legal_name",
              "address",
              "gstin",
              "state_code",
              "invoice_prefix",
            ].map((key) => [key, String(form.get(key))]),
          ),
          delivery_gst_bps: Math.round(Number(form.get("delivery_gst")) * 100),
          franchise_recipients: String(form.get("recipients") ?? "")
            .split(",")
            .map((value) => value.trim())
            .filter(Boolean),
          staff_whatsapp_consent: form.get("staff_consent") === "on",
          approved_for_sales: form.get("approved") === "on",
        };
        void action(() =>
          api("admin/settings", {
            method: "PUT",
            body: JSON.stringify(payload),
          }),
        );
      }}
    >
      <h2>Seller and operations</h2>
      <p>
        Use verified legal and tax details. Provider credentials are managed by
        the operator outside this screen.
      </p>
      <Field
        name="legal_name"
        label="Legal seller name"
        defaultValue={data?.legal_name}
      />
      <Field
        name="address"
        label="Seller address"
        defaultValue={data?.address}
      />
      <Field name="gstin" label="GSTIN" defaultValue={data?.gstin} />
      <Field
        name="state_code"
        label="Two-digit seller state code"
        defaultValue={data?.state_code}
      />
      <Field
        name="invoice_prefix"
        label="Invoice prefix (1–3 uppercase letters)"
        defaultValue={data?.invoice_prefix}
      />
      <Field
        name="delivery_gst"
        label="Delivery GST rate (%)"
        type="number"
        min={0}
        max={40}
        step="0.01"
        defaultValue={data ? data.delivery_gst_bps / 100 : undefined}
      />
      <Field
        name="recipients"
        label="Franchise alert phones, comma separated (+91…)"
        required={false}
        defaultValue={data?.franchise_recipients.join(", ")}
      />
      <label className="checkbox">
        <input
          type="checkbox"
          name="staff_consent"
          defaultChecked={data?.staff_whatsapp_consent}
        />
        All listed staff recipients consent to operational WhatsApp alerts
      </label>
      <label className="checkbox">
        <input
          type="checkbox"
          name="approved"
          defaultChecked={data?.approved_for_sales}
        />
        Seller and tax details have been verified for sales
      </label>
      <button className="button">Save settings</button>
    </form>
  );
}
function Reports() {
  const [data, setData] = useState<Schema["ReportRow"][]>([]);
  const [message, setMessage] = useState("");
  const [download, setDownload] = useState("");
  return (
    <>
      <SalesReport />
      <h2>GST invoice ledger</h2>
      <form
        className="actions"
        onSubmit={async (event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          try {
            setData(
              await api<Schema["ReportRow"][]>(
                `admin/gst-report?start=${form.get("start")}&end=${form.get("end")}`,
              ),
            );
            setMessage("Report loaded.");
            setDownload(
              `/api/v1/admin/gst-report.csv?start=${form.get("start")}&end=${form.get("end")}`,
            );
          } catch (error) {
            setMessage((error as Error).message);
          }
        }}
      >
        <Field name="start" label="From date" type="date" />
        <Field name="end" label="To date" type="date" />
        <button className="button button-small">Load GST report</button>
      </form>
      <Notice message={message} />
      {download && <a href={download}>Download invoice and tax ledger CSV</a>}
      <p>
        CSV order totals repeat on each product row. Review invoices, refunds
        and credit notes with your accountant before filing.
      </p>
      <div
        className="table-scroll"
        tabIndex={0}
        role="region"
        aria-label="GST invoice ledger"
      >
        <table>
          <caption>Paid invoices and processed refunds</caption>
          <thead>
            <tr>
              {[
                "Invoice",
                "Order",
                "Total",
                "CGST",
                "SGST",
                "IGST",
                "Refunded",
              ].map((label) => (
                <th key={label}>{label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.reference}>
                <td>{row.invoice_number}</td>
                <td>{row.reference}</td>
                <td>{money(row.total_paise)}</td>
                <td>{money(row.tax.cgst)}</td>
                <td>{money(row.tax.sgst)}</td>
                <td>{money(row.tax.igst)}</td>
                <td>{money(row.refunded_paise)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
function Media({ action }: { action: Action }) {
  const { data, error } = useLoad<Schema["MediaView"][]>("admin/media");
  return (
    <div className="commerce-grid">
      <form
        className="panel form-stack"
        onSubmit={(event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          void action(() =>
            api(
              "admin/media?alt=" + encodeURIComponent(String(form.get("alt"))),
              { method: "POST", body: form.get("image") as File },
            ),
          );
        }}
      >
        <h2>Upload an image</h2>
        <Field
          name="image"
          label="JPEG, PNG, or WebP (up to 5 MB)"
          type="file"
          accept="image/jpeg,image/png,image/webp"
        />
        <Field name="alt" label="Image description" maxLength={300} />
        <button className="button">Upload image</button>
      </form>
      <section className="panel">
        <h2>Reusable images</h2>
        {!data ? (
          <Load error={error} />
        ) : (
          data.map((item) => (
            <div className="stock-row" key={item.id}>
              <Image
                src={`/api/v1/admin/media/${item.id}`}
                alt={item.alt}
                width={240}
                height={240}
                unoptimized
                className="product-image"
              />
              <p>{item.alt}</p>
              <label className="field">
                Image ID
                <input
                  readOnly
                  value={item.id}
                  onFocus={(event) => event.currentTarget.select()}
                />
              </label>
            </div>
          ))
        )}
      </section>
    </div>
  );
}
