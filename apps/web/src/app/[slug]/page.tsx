import { notFound } from "next/navigation";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
import { PUBLIC_SLUGS, SITE_URL, pathFor } from "@/lib/policy.mjs";
import { JsonLd } from "@/components/JsonLd";
import { EditorialIntro, Faqs } from "@/components/Editorial";
import {
  BranchesEditorial,
  ContactEditorial,
  FranchiseEditorial,
  MenuEditorial,
  StoryEditorial,
} from "@/components/EditorialPages";

export const dynamic = "force-dynamic";
type Props = { params: Promise<{ slug: string }> };
export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  if (!PUBLIC_SLUGS.includes(slug) || slug === "home")
    return { robots: { index: false, follow: false } };
  const page = (await getStorefront()).pages.find((item) => item.slug === slug);
  return page
    ? pageMetadata(page)
    : { robots: { index: false, follow: false } };
}
export default async function PublicPage({ params }: Props) {
  const { slug } = await params;
  if (!PUBLIC_SLUGS.includes(slug) || slug === "home") notFound();
  const content = await getStorefront();
  const page = content.pages.find((item) => item.slug === slug);
  if (!page) notFound();
  return (
    <div className={`editorial-page editorial-page-${slug}`}>
      <JsonLd
        value={{
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          itemListElement: [
            { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
            {
              "@type": "ListItem",
              position: 2,
              name: page.heading,
              item: `${SITE_URL}${pathFor(slug)}`,
            },
          ],
        }}
      />
      <EditorialIntro page={page} />
      {slug === "menu" && <MenuEditorial page={page} content={content} />}
      {slug === "about-us" && <StoryEditorial page={page} content={content} />}
      {slug === "branches" && (
        <BranchesEditorial page={page} content={content} />
      )}
      {slug === "franchise" && (
        <FranchiseEditorial page={page} content={content} />
      )}
      {slug === "contact" && <ContactEditorial page={page} content={content} />}
      <Faqs
        page={page}
        title={
          slug === "franchise"
            ? "Your franchise questions, answered."
            : undefined
        }
      />
    </div>
  );
}
