import { notFound } from "next/navigation";
import { HeroImage } from "@/components/HeroImage";
import { JsonLd } from "@/components/JsonLd";
import { SiteLink } from "@/components/SiteLink";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
import { SITE_URL } from "@/lib/policy.mjs";
import { StructuredPage } from "@/components/StructuredPage";

export const dynamic = "force-dynamic";

export async function generateMetadata() {
  const { pages } = await getStorefront();
  const page = pages.find((item) => item.slug === "home");
  return page ? pageMetadata(page) : {};
}

export default async function Home() {
  const content = await getStorefront();
  const page = content.pages.find((item) => item.slug === "home");
  if (!page) notFound();
  if (page.blocks.length)
    return <StructuredPage blocks={page.blocks} slug="home" />;
  return (
    <>
      <JsonLd
        value={{
          "@context": "https://schema.org",
          "@type": "Organization",
          name: content.brand,
          url: SITE_URL,
        }}
      />
      <section className="container hero">
        <div className="hero-copy">
          <h1>{page.heading}</h1>
          <p className="hero-intro">{page.intro}</p>
          <div className="actions">
            <SiteLink className="button button-primary" href="/menu/">
              Explore the menu <span aria-hidden="true">↗</span>
            </SiteLink>
            <SiteLink className="text-link" href="/branches/">
              Find a store <span aria-hidden="true">→</span>
            </SiteLink>
          </div>
          <div className="hero-note">
            <span className="sun" aria-hidden="true">
              ✳
            </span>
            <p>
              {content.tagline}
              <span>A little spice belongs in every day.</span>
            </p>
          </div>
        </div>
        <HeroImage priority />
      </section>
      <div className="flavour-strip" aria-hidden="true">
        <div className="container">
          <span>Pachi Mirchi</span>
          <span>✳</span>
          <span>Kothimeera</span>
          <span>✳</span>
          <span>Kaju Chicken</span>
          <span>✳</span>
          <span>One more bite.</span>
        </div>
      </div>
      <section className="container section">
        <div className="section-heading">
          <h2>{page.sections[4]?.title}</h2>
          <div>
            <p>{page.sections[4]?.body}</p>
            <SiteLink className="text-link" href="/menu/">
              See the full menu <span aria-hidden="true">↗</span>
            </SiteLink>
          </div>
        </div>
        <div className="featured-menu">
          {content.menu
            .filter((item) => item.featured)
            .slice(0, 3)
            .map((item, index) => (
              <article key={item.slug}>
                <span className="item-number">0{index + 1}</span>
                <span className="dietary">
                  <i aria-hidden="true" /> Non-vegetarian
                </span>
                <h3>{item.name}</h3>
                <p>{item.description}</p>
                <SiteLink href="/menu/" className="text-link">
                  Explore the menu <span aria-hidden="true">→</span>
                </SiteLink>
              </article>
            ))}
        </div>
      </section>
      <section className="story-band">
        <div className="container story-grid">
          <h2>{page.sections[0]?.title}</h2>
          <div>
            <p>{page.sections[0]?.body}</p>
            <SiteLink className="text-link" href="/about-us/">
              A little about us <span aria-hidden="true">↗</span>
            </SiteLink>
          </div>
        </div>
      </section>
      <section className="container section take-home">
        <div className="type-art" aria-hidden="true">
          Good food.
          <br />
          <span>Great mood.</span>
          <span className="art-star">✳</span>
        </div>
        <div>
          <h2>{page.sections[1]?.title}</h2>
          <p>{page.sections[1]?.body}</p>
          <SiteLink className="button" href="/shop/">
            Visit the shop <span aria-hidden="true">↗</span>
          </SiteLink>
        </div>
      </section>
      <section className="container section neighbourhood">
        <div>
          <h2>{page.sections[2]?.title}</h2>
          <p>{page.sections[2]?.body}</p>
          <SiteLink className="button button-primary" href="/branches/">
            Find your snack stop <span aria-hidden="true">↗</span>
          </SiteLink>
        </div>
        <div className="locality-list">
          {content.outlets.map((outlet) => (
            <SiteLink href="/branches/" key={outlet.slug}>
              {outlet.name}
              <span aria-hidden="true">↗</span>
            </SiteLink>
          ))}
        </div>
      </section>
      <section className="franchise-banner">
        <div className="container">
          <div>
            <h2>{page.sections[3]?.title}</h2>
            <p>{page.sections[3]?.body}</p>
          </div>
          <SiteLink className="button" href="/franchise/">
            Let’s talk franchise <span aria-hidden="true">↗</span>
          </SiteLink>
        </div>
      </section>
    </>
  );
}
