import type { MetadataRoute } from "next";
import { indexable, SITE_URL, PRIVATE_PREFIXES } from "@/lib/policy.mjs";

export const dynamic = "force-dynamic";

export default function robots(): MetadataRoute.Robots {
  if (!indexable(process.env))
    return { rules: { userAgent: "*", disallow: "/" } };
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: PRIVATE_PREFIXES.map((prefix) => `/${prefix}/`),
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
