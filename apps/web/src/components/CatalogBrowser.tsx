import { getCatalog } from "@/lib/catalog";
import { money } from "@/lib/commerce";
import { AddToCart } from "@/components/CommerceForms";
import { ProductImage } from "@/components/ProductImage";
import { SiteLink } from "@/components/SiteLink";
import { normalizeCatalogQuery } from "@/lib/catalog-query.mjs";

export const label = (slug: string) =>
  slug
    .split("-")
    .map((word) => word[0]?.toUpperCase() + word.slice(1))
    .join(" ");

export async function CatalogBrowser({
  query,
  category = "",
  tag = "",
}: {
  query: Record<string, string | string[] | undefined>;
  category?: string;
  tag?: string;
}) {
  const filters = normalizeCatalogQuery({
    ...query,
    ...(category ? { category } : {}),
    ...(tag ? { tag } : {}),
  });
  const all = await getCatalog();
  const products = await getCatalog(filters);
  const categories = [
    ...new Set(
      all
        .map((item) => item.product.category)
        .filter((value): value is string => Boolean(value)),
    ),
  ].sort();
  const path = category
    ? `/product-category/${category}/`
    : tag
      ? `/product-tag/${tag}/`
      : "/shop/";
  return (
    <section className="container section catalog-page">
      <nav aria-label="Breadcrumb">
        <SiteLink href="/">Home</SiteLink> /{" "}
        <SiteLink href="/shop/">Shop</SiteLink>
        {(category || tag) && ` / ${label(category || tag)}`}
      </nav>
      <h1>{category || tag ? label(category || tag) : "Shop"}</h1>
      <form method="get" className="actions catalog-filters" action={path}>
        {!tag && filters.tag && (
          <input type="hidden" name="tag" value={filters.tag} />
        )}
        <label className="field">
          Search products
          <input
            name="q"
            type="search"
            defaultValue={filters.q}
            maxLength={100}
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
            <option value="price-asc">Sort by price: low to high</option>
            <option value="price-desc">Sort by price: high to low</option>
            <option value="name">Sort by name</option>
          </select>
        </label>
        <button className="button button-small">Apply filters</button>
        <a href={path}>Reset filters</a>
      </form>
      <p role="status">
        Showing {products.length} {products.length === 1 ? "result" : "results"}
      </p>
      <p>
        Our team confirms delivery and the final total before you pay.{" "}
        <SiteLink href="/cart/">View cart</SiteLink>
      </p>
      {products.length ? (
        <div className="product-grid">
          {products.map((item) => (
            <article className="panel" key={item.id}>
              {(item.media_id || item.product.image) && (
                <a
                  href={`/product/${item.product.slug}/`}
                  aria-label={item.product.name}
                >
                  <ProductImage variant={item} />
                </a>
              )}
              {item.product.category && (
                <a href={`/product-category/${item.product.category}/`}>
                  {label(item.product.category)}
                </a>
              )}
              <h2>
                <a href={`/product/${item.product.slug}/`}>
                  {item.product.name}
                </a>
              </h2>
              <p>
                {item.product.dietary === "veg"
                  ? "Vegetarian"
                  : "Non-vegetarian"}{" "}
                · {item.product.net_quantity}
              </p>
              <p>
                {item.product.compare_at_price_paise &&
                item.product.compare_at_price_paise >
                  item.product.price_paise ? (
                  <>
                    <span className="sr-only">Original price </span>
                    <del>{money(item.product.compare_at_price_paise)}</del>{" "}
                    <span className="sr-only">Current price </span>
                  </>
                ) : null}
                <strong>{money(item.product.price_paise)}</strong>
              </p>
              <AddToCart variant={item} />
            </article>
          ))}
        </div>
      ) : (
        <div className="panel">
          <h2>
            {all.length
              ? "No products match these filters"
              : "We’re preparing our packaged range"}
          </h2>
          <p>
            {all.length
              ? "Reset the filters to see all products."
              : "Products will appear here once their food information and prices are confirmed."}
          </p>
          <SiteLink href="/menu/">Explore the fresh-food menu</SiteLink>
        </div>
      )}
    </section>
  );
}
