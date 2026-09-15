import { notFound } from "next/navigation";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
import { SiteLink } from "@/components/SiteLink";
import { Icon } from "@/components/Icon";
import { MenuGrid } from "@/components/MenuGrid";
import { JsonLd } from "@/components/JsonLd";
import { EnquiryProvider } from "@/components/QuickEnquiry";
import { SITE_URL } from "@/lib/policy.mjs";
export const dynamic = "force-dynamic";
export async function generateMetadata() {
  const content = await getStorefront();
  const page = content.pages.find((item) => item.slug === "home");
  return page ? pageMetadata(page) : {};
}
export default async function Home() {
  const content = await getStorefront();
  if (!content.pages.some((page) => page.slug === "home")) notFound();
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
      <section className="container store-hero signature-hero">
        <div className="store-hero-copy">
          <h1>
            Patnam Pakodi
            <span>
              Four flavours.
              <br />
              One more bite.
            </span>
          </h1>
          <p>
            Red chilli warmth. A green chilli kick. Peppery crunch. Chettinad
            spice. Meet the four chicken pakodi flavours at the heart of our
            menu.
          </p>
          <div className="hero-shopping-actions">
            <SiteLink className="button" href="/menu/">
              Explore the menu <Icon name="arrow" />
            </SiteLink>
            <SiteLink className="button button-outline" href="/branches/">
              Find a branch
            </SiteLink>
          </div>
        </div>
        <div className="store-hero-image signature-hero-image">
          {/* Responsive artwork is built ahead of time to avoid a cold image resize. */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/generated/hero-signature-erra-karam-768.webp"
            srcSet="/generated/hero-signature-erra-karam-384.webp 384w, /generated/hero-signature-erra-karam-768.webp 768w, /generated/hero-signature-erra-karam-1024.webp 1024w"
            alt="Illustration of crisp Erra Karam chicken pakodi"
            width={1024}
            height={1024}
            sizes="(max-width: 767px) 92vw, 50vw"
            fetchPriority="high"
            decoding="async"
          />
          <div className="hero-image-note">
            <span>{content.tagline}</span>
            <Icon name="fresh" />
          </div>
        </div>
      </section>
      <section className="container store-section signature-selection">
        <div className="store-section-heading">
          <div>
            <h2>A flavour for your kind of spice.</h2>
            <p>Get to know our four signature chicken pakodi flavours.</p>
          </div>
          <SiteLink className="text-link" href="/menu/">
            View the menu <Icon name="arrow" />
          </SiteLink>
        </div>
        <MenuGrid items={content.menu} />
      </section>
      <section className="signature-story">
        <div className="container signature-story-inner">
          <h2>
            A little spice.
            <br />A lot of good company.
          </h2>
          <div>
            <p>
              An evening catch-up. A snack with friends. That familiar craving
              for something crisp and spicy. Make a little room for Patnam
              Pakodi.
            </p>
            <SiteLink className="text-link" href="/about-us/">
              Our story <Icon name="arrow" />
            </SiteLink>
          </div>
        </div>
      </section>
      <section className="container store-section signature-visit">
        <div>
          <h2>Find your local Patnam.</h2>
          <p>Explore our branches and plan your next snack break.</p>
        </div>
        <SiteLink className="button" href="/branches/">
          <Icon name="pin" />
          Find a branch <Icon name="arrow" />
        </SiteLink>
      </section>
      <EnquiryProvider>
        <section className="container franchise-invitation">
          <div>
            <h2>Bring the flavour to your neighbourhood.</h2>
            <p>
              Explore four franchise formats and find the right fit for your
              idea.
            </p>
          </div>
          <div className="actions">
            <SiteLink href="/franchise/" className="button button-outline">
              Explore franchise <Icon name="arrow" />
            </SiteLink>
            <button className="text-link" data-enquiry="Download Brochure">
              Download brochure
            </button>
          </div>
        </section>
      </EnquiryProvider>
    </>
  );
}
