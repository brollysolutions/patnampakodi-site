import { SiteLink } from "@/components/SiteLink";
import { notFound } from "next/navigation";
import { getCatalog } from "@/lib/catalog";
import { money } from "@/lib/commerce";
import { AddToCart } from "@/components/CommerceForms";
import { JsonLd } from "@/components/JsonLd";
import { pageMetadata } from "@/lib/seo";
import Image from "next/image";
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
    slug: "shop/" + product.slug,
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
      <SiteLink href="/shop/">Back to shop</SiteLink>
      <h1>{product.name}</h1>
      {item.media_id && (
        <Image
          className="product-image product-image-detail"
          src={`/api/v1/media/${item.media_id}`}
          alt={product.name}
          width={800}
          height={600}
          unoptimized
        />
      )}
      <p>{product.description}</p>
      <p>
        {product.dietary === "veg" ? "Vegetarian" : "Non-vegetarian"} ·{" "}
        {product.net_quantity}
      </p>
      <p>
        <strong>{money(product.price_paise)}</strong> including applicable tax.
        Delivery is quoted before payment.
      </p>
      <AddToCart variant={item} />
      <SiteLink className="button button-small" href="/cart/">
        View cart
      </SiteLink>
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
            url: `https://patnampakodi.com/shop/${product.slug}/`,
          },
        }}
      />
    </section>
  );
}
