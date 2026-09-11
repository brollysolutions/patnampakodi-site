import { SiteLink } from "@/components/SiteLink";
import { notFound } from "next/navigation";
import { getCatalog } from "@/lib/catalog";
import { money } from "@/lib/commerce";
import { AddToCart, FavouriteButton } from "@/components/ProductActions";
import { DeliveryCheck } from "@/components/DeliveryCheck";
import { ProductCard } from "@/components/ProductCard";
import { Icon } from "@/components/Icon";
import { JsonLd } from "@/components/JsonLd";
import { pageMetadata } from "@/lib/seo";
import { ProductImage } from "@/components/ProductImage";
import { label } from "@/components/CatalogBrowser";
type Props = { params: Promise<{ product: string }> };
export const dynamic = "force-dynamic";
async function find(props: Props) {
  const { product } = await props.params;
  const item = (await getCatalog()).find(
    (item) => item.product.slug === product,
  );
  if (!item) notFound();
  return item;
}
export async function generateMetadata(props: Props) {
  const { product } = await find(props);
  return pageMetadata({
    slug: "product/" + product.slug,
    title: product.name + " | Patnam Pakodi",
    description: product.description.slice(0, 155),
    heading: product.name,
    intro: product.description,
    sections: [],
    blocks: [],
  });
}
export default async function ProductPage(props: Props) {
  const item = await find(props);
  const product = item.product;
  const related = (await getCatalog({ mode: product.mode }))
    .filter((entry) => entry.id !== item.id)
    .slice(0, 4);
  return (
    <section className="container section">
      <nav className="store-breadcrumb" aria-label="Breadcrumb">
        <SiteLink href="/">Home</SiteLink> /{" "}
        <SiteLink href={product.mode === "fresh" ? "/menu/" : "/shop/"}>
          {product.mode === "fresh" ? "Order fresh" : "Shop"}
        </SiteLink>{" "}
        / {product.name}
      </nav>
      <div className="product-detail-grid">
        <div className="product-detail-image">
          <ProductImage variant={item} priority />
          <FavouriteButton variant={item} />
        </div>
        <div className="form-stack">
          <p className="eyebrow">
            {product.mode === "fresh"
              ? "Fresh from our kitchen"
              : "Patnam Pakodi at home"}
          </p>
          <h1>{product.name}</h1>
          <p>{product.description}</p>
          <p>
            {product.dietary === "veg" ? "Vegetarian" : "Non-vegetarian"} ·{" "}
            {product.net_quantity}
          </p>
          <p>
            {product.compare_at_price_paise &&
            product.compare_at_price_paise > product.price_paise ? (
              <>
                <span className="sr-only">Original price </span>
                <del>{money(product.compare_at_price_paise)}</del>{" "}
                <span className="sr-only">Current price </span>
              </>
            ) : null}
            <strong>{money(product.price_paise)}</strong> including applicable
            tax. Delivery is calculated at checkout.
          </p>
          <AddToCart variant={item} quantityInput />
          <SiteLink
            className="button button-small button-outline"
            href={`/cart/?mode=${product.mode}`}
          >
            View cart
          </SiteLink>
          <DeliveryCheck mode={product.mode} />
          <p className="summary-note">
            <Icon name="shield" /> Guest checkout · Secure payment
          </p>
          {product.category && (
            <p>
              Category:{" "}
              <a href={`/product-category/${product.category}/`}>
                {label(product.category)}
              </a>
            </p>
          )}
          {Boolean(product.tags?.length) && (
            <p>
              Tags:{" "}
              {product.tags?.map((tag, index) => (
                <span key={tag}>
                  {index > 0 ? ", " : ""}
                  <a href={`/product-tag/${tag}/`}>{label(tag)}</a>
                </span>
              ))}
            </p>
          )}
        </div>
      </div>
      <h2>Product information</h2>
      <dl className="panel facts">
        {(
          [
            "ingredients",
            "allergens",
            "nutrition",
            "net_quantity",
            "shelf_life",
            "manufacturer",
            "consumer_care",
          ] as const
        )
          .filter((field) => product[field])
          .map((field) => (
            <div key={field}>
              <dt>{field.replaceAll("_", " ")}</dt>
              <dd>{product[field]}</dd>
            </div>
          ))}
      </dl>
      {related.length > 0 && (
        <section className="store-section">
          <div className="store-section-heading">
            <h2>Make room for one more</h2>
            <SiteLink
              className="text-link"
              href={product.mode === "fresh" ? "/menu/" : "/shop/"}
            >
              Explore the range
              <Icon name="arrow" />
            </SiteLink>
          </div>
          <div className="store-product-grid">
            {related.map((entry) => (
              <ProductCard key={entry.id} item={entry} />
            ))}
          </div>
        </section>
      )}
      <JsonLd
        value={{
          "@context": "https://schema.org",
          "@type": "Product",
          name: product.name,
          description: product.description,
          sku: item.sku,
          offers: {
            "@type": "Offer",
            priceCurrency: "INR",
            price: (product.price_paise / 100).toFixed(2),
            availability:
              item.stock > item.reserved
                ? "https://schema.org/InStock"
                : "https://schema.org/OutOfStock",
            url: `https://patnampakodi.com/product/${product.slug}/`,
          },
        }}
      />
    </section>
  );
}
