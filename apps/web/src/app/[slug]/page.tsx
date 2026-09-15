import Image from "next/image";
import { notFound } from "next/navigation";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
import { PUBLIC_SLUGS, SITE_URL, pathFor } from "@/lib/policy.mjs";
import { SiteLink } from "@/components/SiteLink";
import { MenuGrid } from "@/components/MenuGrid";
import { JsonLd } from "@/components/JsonLd";
import { Icon } from "@/components/Icon";
import { FranchiseForm } from "@/components/FranchiseForm";
import { EnquiryProvider } from "@/components/QuickEnquiry";
import { money } from "@/lib/commerce";

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
    <>
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
      <section className="container page-intro signature-intro">
        <div>
          <SiteLink href="/" className="breadcrumb">
            Home /
          </SiteLink>
          <h1>{page.heading}</h1>
          <p>{page.intro}</p>
        </div>
      </section>
      {slug === "menu" && (
        <section
          className="container signature-menu"
          aria-label="Our four signature flavours"
        >
          <MenuGrid items={content.menu} headingLevel={2} />
          <div className="menu-visit-note">
            <p>
              All four flavours are chicken pakodi. Food illustrations are
              representative. Please ask our team about ingredients and
              allergens.
            </p>
            <SiteLink className="button" href="/branches/">
              Find a branch <Icon name="arrow" />
            </SiteLink>
          </div>
        </section>
      )}
      {slug === "about-us" && (
        <section className="container section signature-about">
          <Image
            src="/images/live/signature-pachi-mirchi.webp"
            alt="Illustration of Pachi Mirchi chicken pakodi"
            width={1024}
            height={1024}
            sizes="(max-width: 767px) 92vw, 45vw"
          />
          <div className="form-stack">
            {page.sections.map((section) => (
              <section key={section.title}>
                <h2>{section.title}</h2>
                <p>{section.body}</p>
              </section>
            ))}
            <SiteLink className="text-link" href="/menu/">
              Meet the four flavours <Icon name="arrow" />
            </SiteLink>
          </div>
        </section>
      )}
      {slug === "branches" && (
        <section className="container section">
          <div className="outlet-grid">
            {content.outlets.map((outlet) => (
              <article className="panel form-stack" key={outlet.slug}>
                <Icon name="pin" />
                <h2>{outlet.name}</h2>
                <p>
                  {outlet.city} · {outlet.pincode}
                </p>
                {outlet.address && <p>{outlet.address}</p>}
                {outlet.hours && <p>{outlet.hours}</p>}
                <SiteLink
                  className="text-link"
                  href={`/branches/${outlet.slug}/`}
                >
                  Branch details <Icon name="arrow" />
                </SiteLink>
                <a
                  href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`Patnam Pakodi ${outlet.name} ${outlet.city}`)}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Look up on Google Maps{" "}
                  <span className="sr-only">(opens a new tab)</span>
                </a>
              </article>
            ))}
          </div>
          {!content.outlets.length && (
            <p>Contact our team for current branch locations.</p>
          )}
          <p className="model-note">
            Check the current address and opening hours on the branch’s map
            listing before you travel.
          </p>
        </section>
      )}
      {slug === "franchise" && (
        <>
          <section className="container section franchise-models">
            <h2>Choose your format.</h2>
            <div className="model-grid signature-models">
              {content.franchise_models.map((model, index) => (
                <article key={model.name}>
                  <div>
                    <span className="franchise-number" aria-hidden="true">
                      0{index + 1}
                    </span>
                    <h3>{model.name}</h3>
                    {model.investment_paise != null && (
                      <p className="franchise-price">
                        {money(model.investment_paise)}
                      </p>
                    )}
                    <p>{model.description}</p>
                  </div>
                </article>
              ))}
            </div>
            <p className="model-note">
              Package details are from our franchise brochure. Customized
              inclusions may change the price. Discuss the location, inclusions
              and operating terms with our team.
            </p>
          </section>
          <section className="container section franchise-inclusions">
            <h2>What comes with your setup?</h2>
            {page.sections.map((section) => (
              <details key={section.title}>
                <summary>{section.title}</summary>
                <p>{section.body}</p>
              </details>
            ))}
            <EnquiryProvider>
              <button
                className="button button-outline"
                data-enquiry="Download Brochure"
              >
                Download brochure <Icon name="arrow" />
              </button>
            </EnquiryProvider>
          </section>
          <section className="container section franchise-enquiry-layout">
            <div>
              <h2>Let’s shape your next step.</h2>
              <p>
                Tell us where you would like to open and which format interests
                you. Our team will help you explore the details.
              </p>
              {content.contact_phone && (
                <a className="text-link" href={`tel:${content.contact_phone}`}>
                  Call our franchise team <Icon name="phone" />
                </a>
              )}
            </div>
            <FranchiseForm />
          </section>
        </>
      )}
      {slug === "contact" && (
        <section className="container section contact-grid">
          <div className="contact-card form-stack">
            <h2>A good conversation starts here.</h2>
            {content.contact_phone && (
              <a className="text-link" href={`tel:${content.contact_phone}`}>
                <Icon name="phone" />
                +91 90003 65219
              </a>
            )}
            {content.contact_email && (
              <a
                className="contact-email"
                href={`mailto:${content.contact_email}`}
              >
                {content.contact_email}
              </a>
            )}
            {content.contact_phone && (
              <a
                className="button"
                href={`https://wa.me/${content.contact_phone.replace("+", "")}`}
                target="_blank"
                rel="noreferrer"
              >
                Contact on WhatsApp{" "}
                <span className="sr-only">(opens a new tab)</span>
                <Icon name="arrow" />
              </a>
            )}
            <a
              href="https://www.instagram.com/patnampakodi/"
              target="_blank"
              rel="noreferrer"
            >
              Instagram: @patnampakodi{" "}
              <span className="sr-only">(opens a new tab)</span>
            </a>
          </div>
          <div className="contact-directions form-stack">
            {page.sections.map((section) => (
              <section key={section.title}>
                <h2>{section.title}</h2>
                <p>{section.body}</p>
              </section>
            ))}
            <SiteLink className="text-link" href="/branches/">
              Looking for a snack? Find a branch <Icon name="arrow" />
            </SiteLink>
            <SiteLink className="text-link" href="/franchise/">
              Explore franchise formats <Icon name="arrow" />
            </SiteLink>
          </div>
        </section>
      )}
    </>
  );
}
