import { SiteLink } from "@/components/SiteLink";
import { notFound } from "next/navigation";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
import { RETIRED_OUTLETS, SITE_URL } from "@/lib/policy.mjs";
import {
  BranchCard,
  Faqs,
  FranchiseInvitation,
  Paragraphs,
} from "@/components/Editorial";
import { JsonLd } from "@/components/JsonLd";
import { Icon } from "@/components/Icon";

type Props = { params: Promise<{ outlet: string }> };
export const dynamic = "force-dynamic";
function retiredName(slug: string) {
  return Object.hasOwn(RETIRED_OUTLETS, slug)
    ? RETIRED_OUTLETS[slug as keyof typeof RETIRED_OUTLETS]
    : null;
}
export async function generateMetadata({ params }: Props) {
  const { outlet: slug } = await params;
  const name = retiredName(slug);
  if (name)
    return {
      title: `${name} branch update | Patnam Pakodi`,
      description:
        "Patnam Pakodi is currently serving only in Kukatpally. Find our current branch details and four-flavour menu.",
      alternates: { canonical: `${SITE_URL}/branches/${slug}/` },
      robots: { index: false, follow: true },
    };
  const outlet = (await getStorefront()).outlets.find(
    (item) => item.slug === slug,
  );
  if (!outlet) return { robots: { index: false, follow: false } };
  return pageMetadata({
    slug: `branches/${slug}`,
    title: "Visit Kukatpally | Patnam Pakodi Chicken Pakodi",
    description:
      "Plan a visit to Patnam Pakodi, Kukatpally, our only serving branch. Find the listed address, hours and contact number, plus our four chicken pakodi flavours.",
    heading: outlet.name,
    intro: "",
    sections: [],
    blocks: [],
  });
}
export default async function OutletPage({ params }: Props) {
  const { outlet: slug } = await params;
  const name = retiredName(slug);
  if (name)
    return (
      <div className="editorial-page">
        <section className="container editorial-section editorial-prose">
          <SiteLink href="/branches/">Current branch information</SiteLink>
          <h1>{name} branch update.</h1>
          <p>
            We are currently serving only at our Kukatpally branch in Hyderabad.
            This older {name} listing does not represent a currently serving
            branch.
          </p>
          <div className="actions">
            <SiteLink className="button" href="/branches/kukatpally/">
              Visit Kukatpally <Icon name="arrow" />
            </SiteLink>
            <SiteLink className="text-link" href="/menu/">
              Explore our four flavours
            </SiteLink>
          </div>
        </section>
      </div>
    );
  const content = await getStorefront();
  const outlet = content.outlets.find((item) => item.slug === slug);
  if (!outlet) notFound();
  const page = content.pages.find((item) => item.slug === "branches");
  return (
    <div className="editorial-page">
      <section className="container editorial-intro">
        <SiteLink href="/branches/" className="breadcrumb">
          Branches /
        </SiteLink>
        <div>
          <h1>
            Patnam Pakodi,
            <br />
            Kukatpally.
          </h1>
          <p>
            Our only serving branch, in Hyderabad. Get to know the four
            flavours, check the visit details and make time for a pakodi break.
          </p>
        </div>
      </section>
      <section className="container editorial-section editorial-branch-layout">
        <BranchCard outlet={outlet} detail />
        <div className="editorial-prose">
          {page?.sections.map((section) => (
            <section key={section.title}>
              <h2>{section.title}</h2>
              <Paragraphs text={section.body} />
            </section>
          ))}
          <SiteLink href="/menu/" className="text-link">
            Meet the four flavours <Icon name="arrow" />
          </SiteLink>
          <p>
            For central or franchise enquiries, use the office details on our
            Contact page.
          </p>
          <SiteLink href="/contact/" className="text-link">
            Contact our central team <Icon name="arrow" />
          </SiteLink>
        </div>
      </section>
      <JsonLd
        value={{
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          itemListElement: [
            { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
            {
              "@type": "ListItem",
              position: 2,
              name: "Branches",
              item: `${SITE_URL}/branches/`,
            },
            {
              "@type": "ListItem",
              position: 3,
              name: "Kukatpally",
              item: `${SITE_URL}/branches/kukatpally/`,
            },
          ],
        }}
      />
      <FranchiseInvitation />
      {page && <Faqs page={page} />}
    </div>
  );
}
