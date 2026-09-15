import { notFound } from "next/navigation";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
import { SiteLink } from "@/components/SiteLink";
import { Icon } from "@/components/Icon";
import { MenuGrid } from "@/components/MenuGrid";
import { JsonLd } from "@/components/JsonLd";
import {
  EditorialTable,
  Faqs,
  FoodPortrait,
  FranchiseInvitation,
  VisitInvitation,
} from "@/components/Editorial";
import { SITE_URL } from "@/lib/policy.mjs";

export const dynamic = "force-dynamic";
export async function generateMetadata() {
  const page = (await getStorefront()).pages.find(
    (item) => item.slug === "home",
  );
  return page ? pageMetadata(page) : {};
}
export default async function Home() {
  const content = await getStorefront();
  const page = content.pages.find((item) => item.slug === "home");
  if (!page) notFound();
  return (
    <div className="editorial-page">
      <JsonLd
        value={{
          "@context": "https://schema.org",
          "@type": "Organization",
          name: content.brand,
          url: SITE_URL,
        }}
      />
      <section className="container editorial-home-intro">
        <h1>
          Chicken pakodi.
          <br />
          Full of character.
        </h1>
        <div>
          <p>{page.intro}</p>
          <div className="actions">
            <SiteLink className="button" href="/menu/">
              Explore the four flavours <Icon name="arrow" />
            </SiteLink>
            <SiteLink className="text-link" href="/branches/">
              Visit Kukatpally
            </SiteLink>
          </div>
        </div>
      </section>
      <div className="container">
        <EditorialTable hero />
      </div>
      <section className="container editorial-section editorial-selection">
        <div className="editorial-section-heading">
          <h2>
            A flavour for
            <br />
            your kind of spice.
          </h2>
          <div>
            <p>
              Red chilli warmth. A green chilli kick. Peppery crunch. Chettinad
              spice. Four dry chicken pakodis, each with a character of its own.
            </p>
            <SiteLink className="text-link" href="/menu/">
              Read the flavour guide <Icon name="arrow" />
            </SiteLink>
          </div>
        </div>
        <MenuGrid items={content.menu} />
      </section>
      <section className="editorial-home-story">
        <div className="container editorial-section">
          <FoodPortrait
            image="/images/live/signature-miriyala.webp"
            alt="Representative illustration of dry pepper chicken pakodi"
          />
          <div>
            <h2>
              From a love of pakodi.
              <br />
              For the moments
              <br />
              we share.
            </h2>
            <p>
              Rooted in Guntur-style chicken pakodi and at home in Hyderabad,
              Patnam Pakodi brings a little spice to the everyday. A catch-up, a
              craving, a pause in your day.
            </p>
            <p>
              Our story is about the food and the people who make time for it.
              Right now, you can find us in Kukatpally.
            </p>
            <SiteLink className="text-link" href="/about-us/">
              The story behind Patnam <Icon name="arrow" />
            </SiteLink>
          </div>
        </div>
      </section>
      <VisitInvitation content={content} />
      <FranchiseInvitation />
      <Faqs page={page} />
    </div>
  );
}
