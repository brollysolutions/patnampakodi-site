import { SiteLink } from "@/components/SiteLink";
import { getCatalog } from "@/lib/catalog";
import { money } from "@/lib/commerce";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
import { AddToCart } from "@/components/CommerceForms";
import Image from "next/image";
export const dynamic = "force-dynamic";
export async function generateMetadata() {
  const content = await getStorefront();
  const page = content.pages.find((page) => page.slug === "shop");
  return page
    ? pageMetadata(page)
    : { title: "Packaged products | Patnam Pakodi" };
}
export default async function Shop({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | undefined>>;
}) {
  const query = await searchParams;
  const all = await getCatalog();
  const max = Number(query.max ?? 0);
  const products = all.filter(
    (item) =>
      (!query.dietary || item.product.dietary === query.dietary) &&
      (!max || item.product.price_paise <= max * 100),
  );
  return (
    <section className="container section">
      <h1>Bring the crunch home.</h1>
      <p>
        Packaged products, delivered by our team. We confirm delivery and the
        final total before you pay.
      </p>
      <SiteLink className="button button-small" href="/cart/">
        View cart
      </SiteLink>
      <form method="get" className="actions">
        <label className="field">
          Category
          <select name="dietary" defaultValue={query.dietary ?? ""}>
            <option value="">All products</option>
            <option value="veg">Vegetarian</option>
            <option value="non-veg">Non-vegetarian</option>
          </select>
        </label>
        <label className="field">
          Maximum price in INR
          <input name="max" type="number" min="0" defaultValue={query.max} />
        </label>
        <button className="button button-small">Apply filters</button>
        <SiteLink href="/shop/">Reset filters</SiteLink>
      </form>
      {products.length ? (
        <div className="product-grid">
          {products.map((item) => (
            <article className="panel" key={item.id}>
              {item.media_id && (
                <Image
                  className="product-image"
                  src={`/api/v1/media/${item.media_id}`}
                  alt={item.product.name}
                  width={640}
                  height={480}
                  unoptimized
                />
              )}
              <h2>
                <a href={`/shop/${item.product.slug}/`}>{item.product.name}</a>
              </h2>
              <p>{item.product.description}</p>
              <p>
                {item.product.dietary === "veg"
                  ? "Vegetarian"
                  : "Non-vegetarian"}{" "}
                · {item.product.net_quantity}
              </p>
              <p>
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
