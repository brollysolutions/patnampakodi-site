import type { MetadataRoute } from "next";
import { getStorefront } from "@/lib/content";
import { getCatalog } from "@/lib/catalog";
import { SITE_URL, PUBLIC_SLUGS, pathFor, indexable } from "@/lib/policy.mjs";

export const dynamic = "force-dynamic";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  if (!indexable(process.env)) return [];
  const content = await getStorefront();
  const catalog = content.ordering_enabled ? await getCatalog() : [];
  return [
    ...content.pages.filter(
      (page) =>
        PUBLIC_SLUGS.includes(page.slug) ||
        /^policies\/[a-z0-9-]+$/.test(page.slug),
    ),
    ...content.outlets.map((item) => ({ slug: "branches/" + item.slug })),
    ...catalog.map((item) => ({ slug: "product/" + item.product.slug })),
    ...[
      ...new Set(catalog.map((item) => item.product.category).filter(Boolean)),
    ].map((category) => ({ slug: "product-category/" + category })),
    ...[...new Set(catalog.flatMap((item) => item.product.tags ?? []))].map(
      (tag) => ({ slug: "product-tag/" + tag }),
    ),
  ].map((page) => ({
    url: `${SITE_URL}${pathFor(page.slug)}`,
    lastModified: content.revision,
  }));
}
