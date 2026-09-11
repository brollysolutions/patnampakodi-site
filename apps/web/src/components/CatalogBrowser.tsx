import { getCatalog } from "@/lib/catalog";
import { normalizeCatalogQuery } from "@/lib/catalog-query.mjs";
import { SiteLink } from "./SiteLink";
import { ProductCard } from "./ProductCard";
import { DeliveryCheck } from "./DeliveryCheck";
import { CatalogFilters } from "./CatalogFilters";
import { Icon } from "./Icon";
import type { ShoppingMode } from "@/lib/shopping";
export const label = (slug: string) =>
  slug
    .split("-")
    .map((word) => word[0]?.toUpperCase() + word.slice(1))
    .join(" ");
export async function CatalogBrowser({
  query,
  category = "",
  tag = "",
  mode = "packaged",
}: {
  query: Record<string, string | string[] | undefined>;
  category?: string;
  tag?: string;
  mode?: ShoppingMode;
}) {
  const filters = normalizeCatalogQuery({
    ...query,
    ...(category ? { category } : {}),
    ...(tag ? { tag } : {}),
  });
  const [all, products] = await Promise.all([
    getCatalog({ mode: category || tag ? undefined : mode }),
    getCatalog({ ...filters, mode: category || tag ? undefined : mode }),
  ]);
  const categories = [
    ...new Set(all.map((item) => item.product.category).filter(Boolean)),
  ].sort();
  const path = category
    ? `/product-category/${category}/`
    : tag
      ? `/product-tag/${tag}/`
      : mode === "fresh"
        ? "/menu/"
        : "/shop/";
  return (
    <section className="container shop-page">
      <nav className="store-breadcrumb" aria-label="Breadcrumb">
        <SiteLink href="/">Home</SiteLink>
        <Icon name="chevron" />
        <span>
          {category || tag
            ? label(category || tag)
            : mode === "fresh"
              ? "Order fresh"
              : "Shop packaged"}
        </span>
      </nav>
      <div className="shop-heading">
        <div>
          <h1>
            {category || tag
              ? label(category || tag)
              : mode === "fresh"
                ? "Order fresh pakodi."
                : "Shop packaged favourites."}
          </h1>
          <p>
            {mode === "fresh"
              ? "Explore the menu. Choose your bites. We’ll take care of the cooking."
              : "Your favourite pakodi flavours, ready for your own kitchen."}
          </p>
        </div>
        <DeliveryCheck mode={mode} />
      </div>
      <div className="catalog-layout">
        <CatalogFilters>
          <form method="get" action={path} className="form-stack">
            {tag && <input type="hidden" name="tag" value={tag} />}
            <label className="field">
              Search products
              <input
                name="q"
                type="search"
                defaultValue={filters.q}
                maxLength={100}
                placeholder="What sounds good?"
              />
            </label>
            {!category && (
              <label className="field">
                Category
                <select name="category" defaultValue={filters.category}>
                  <option value="">All categories</option>
                  {categories.map((value) => (
                    <option key={value} value={value}>
                      {label(value)}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <label className="field">
              Dietary preference
              <select name="dietary" defaultValue={filters.dietary}>
                <option value="">All products</option>
                <option value="veg">Vegetarian</option>
                <option value="non-veg">Non-vegetarian</option>
              </select>
            </label>
            <label className="field">
              Maximum price in INR
              <input
                name="max"
                type="number"
                min="0"
                step="0.01"
                defaultValue={
                  filters.max_price == null ? "" : filters.max_price / 100
                }
              />
            </label>
            <label className="field">
              Shop order
              <select name="sort" defaultValue={filters.sort}>
                <option value="default">Default sorting</option>
                <option value="price-asc">Price: low to high</option>
                <option value="price-desc">Price: high to low</option>
                <option value="name">Name: A to Z</option>
              </select>
            </label>
            <button className="button">Apply filters</button>
            <a href={path} className="reset-link">
              Reset filters
            </a>
          </form>
        </CatalogFilters>
        <div>
          <div className="catalog-results">
            <p role="status">
              {products.length} {products.length === 1 ? "result" : "results"}
              {filters.q && <> for “{filters.q}”</>}
            </p>
            <SiteLink href={`/cart/?mode=${mode}`}>
              View cart <Icon name="arrow" />
            </SiteLink>
          </div>
          {(filters.q ||
            filters.category ||
            filters.dietary ||
            filters.max_price != null) && (
            <div className="active-filters">
              {[
                filters.q,
                filters.category && label(filters.category),
                filters.dietary &&
                  (filters.dietary === "veg" ? "Vegetarian" : "Non-vegetarian"),
                filters.max_price != null &&
                  `Up to ₹${filters.max_price / 100}`,
              ]
                .filter(Boolean)
                .map((value) => (
                  <span key={String(value)}>{value}</span>
                ))}
              <a href={path}>Clear all</a>
            </div>
          )}
          {products.length ? (
            <div className="store-product-grid">
              {products.map((item) => (
                <ProductCard item={item} key={item.id} headingLevel={2} />
              ))}
            </div>
          ) : (
            <div className="store-empty">
              <Icon name={all.length ? "search" : "box"} />
              <h2>
                {all.length
                  ? "No products match these filters"
                  : mode === "fresh"
                    ? "Fresh ordering is on its way"
                    : "We’re preparing our packaged range"}
              </h2>
              <p>
                {all.length
                  ? "Try another search or clear your filters to explore the range."
                  : "We’re confirming the range and delivery details. In the meantime, explore Patnam Pakodi at an outlet near you."}
              </p>
              <SiteLink
                className="button button-outline"
                href={all.length ? path : "/branches/"}
              >
                {all.length ? "Clear filters" : "Find a branch"}
                <Icon name="arrow" />
              </SiteLink>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
