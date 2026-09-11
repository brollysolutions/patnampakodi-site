import { ProductImage } from "./ProductImage";
import { AddToCart, FavouriteButton } from "./ProductActions";
import { Icon } from "./Icon";
import { money, type Schema } from "@/lib/commerce";
export function ProductCard({
  item,
  headingLevel = 3,
}: {
  item: Schema["VariantView"];
  headingLevel?: 2 | 3;
}) {
  const product = item.product;
  const Heading = headingLevel === 2 ? "h2" : "h3";
  return (
    <article className="store-product-card">
      <div className="store-product-media">
        <a href={`/product/${product.slug}/`} aria-label={product.name}>
          {item.media_id || product.image ? (
            <ProductImage variant={item} />
          ) : (
            <span className="product-no-image">
              <Icon name="box" />
              <span>{product.net_quantity}</span>
            </span>
          )}
        </a>
        <FavouriteButton variant={item} />
      </div>
      <div className="store-product-body">
        <p className="product-meta">
          <span className={`diet-mark ${product.dietary}`} aria-hidden="true" />
          {product.dietary === "veg" ? "Vegetarian" : "Non-vegetarian"}
          <span>·</span>
          {product.net_quantity}
        </p>
        <Heading>
          <a href={`/product/${product.slug}/`}>{product.name}</a>
        </Heading>
        <p className="product-price">
          {product.compare_at_price_paise &&
          product.compare_at_price_paise > product.price_paise ? (
            <del>
              <span className="sr-only">Previous price </span>
              {money(product.compare_at_price_paise)}
            </del>
          ) : null}
          <strong>{money(product.price_paise)}</strong>
        </p>
        <AddToCart variant={item} />
      </div>
    </article>
  );
}
