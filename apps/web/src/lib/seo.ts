import type { Metadata } from "next";
import type { PageContent } from "./content";
import { SITE_URL, pathFor } from "./policy.mjs";

export function pageMetadata(page: PageContent): Metadata {
  const url = `${SITE_URL}${pathFor(page.slug)}`;
  return {
    title: page.title,
    description: page.description,
    alternates: { canonical: url },
    openGraph: {
      title: page.title,
      description: page.description,
      url,
      type: "website",
      images: [
        {
          url: `${SITE_URL}/opengraph-image`,
          width: 1200,
          height: 630,
          alt: "Patnam Pakodi — Life Lo Spice Undali",
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: page.title,
      description: page.description,
      images: [`${SITE_URL}/opengraph-image`],
    },
  };
}
