import Image from "next/image";
import { Icon } from "./Icon";
import type { Schema } from "@/lib/commerce";
export function ProductImage({
  variant,
  priority = false,
}: {
  variant: Schema["VariantView"];
  priority?: boolean;
}) {
  const source = variant.media_id
    ? `/api/v1/media/${variant.media_id}`
    : variant.product.image;
  if (!source)
    return (
      <span
        className="product-image product-image-placeholder"
        aria-hidden="true"
      >
        <Icon name="box" />
      </span>
    );
  return (
    <Image
      className="product-image"
      src={source}
      alt={variant.product.name}
      width={800}
      height={800}
      sizes="(max-width: 700px) 90vw, 40vw"
      priority={priority}
      unoptimized={Boolean(variant.media_id)}
    />
  );
}
