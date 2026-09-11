import { SiteLink } from "@/components/SiteLink";
import { notFound } from "next/navigation";
import { getCatalog } from "@/lib/catalog";
import { money } from "@/lib/commerce";
import { AddToCart } from "@/components/CommerceForms";
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
  return (
    <section className="container section">
      <nav aria-label="Breadcrumb">
        <SiteLink href="/">Home</SiteLink> /{" "}
        <SiteLink href="/shop/">Shop</SiteLink> / {product.name}
      </nav>
      <div className="product-detail-grid">
        {(item.media_id || product.image) && (
          <div>
            <ProductImage variant={item} priority />
          </div>
        )}
        <div className="form-stack">
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
            tax. Delivery is quoted before payment.
          </p>
          <AddToCart variant={item} quantityInput />
          <SiteLink className="button button-small" href="/cart/">
            View cart
          </SiteLink>
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
        ).map((field) => (
          <div key={field}>
            <dt>{field.replaceAll("_", " ")}</dt>
            <dd>{product[field]}</dd>
          </div>
        ))}
      </dl>
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
