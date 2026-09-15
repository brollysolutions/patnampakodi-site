import Image from "next/image";
import type { PageContent, Storefront, Outlet } from "@/lib/content";
import { SiteLink } from "./SiteLink";
import { Icon } from "./Icon";
import { JsonLd } from "./JsonLd";
import { EnquiryProvider } from "./QuickEnquiry";

export function Paragraphs({ text }: { text: string }) {
  return (
    <>
      {text.split(/\n\n+/).map((paragraph) => (
        <p key={paragraph}>{paragraph}</p>
      ))}
    </>
  );
}

export function Faqs({
  page,
  title = "A few things you might be wondering.",
}: {
  page: PageContent;
  title?: string;
}) {
  const faqs = page.blocks.filter((block) => block.kind === "faq");
  if (!faqs.length) return null;
  return (
    <section className="container editorial-section editorial-faq">
      <div className="editorial-faq-intro">
        <h2>{title}</h2>
        <p>A little more detail, before you visit or take your next step.</p>
        <SiteLink className="text-link" href="/contact/">
          Talk to our team <Icon name="arrow" />
        </SiteLink>
      </div>
      <div className="editorial-faq-list">
        {faqs.map((faq) => (
          <details open key={faq.title}>
            <summary>
              {faq.title}
              <span aria-hidden="true" className="faq-indicator" />
            </summary>
            <div>
              <Paragraphs text={faq.text} />
            </div>
          </details>
        ))}
      </div>
      <JsonLd
        value={{
          "@context": "https://schema.org",
          "@type": "FAQPage",
          mainEntity: faqs.map((faq) => ({
            "@type": "Question",
            name: faq.title,
            acceptedAnswer: { "@type": "Answer", text: faq.text },
          })),
        }}
      />
    </section>
  );
}

export function EditorialIntro({ page }: { page: PageContent }) {
  return (
    <section className="container editorial-intro">
      <SiteLink className="breadcrumb" href="/">
        Home /
      </SiteLink>
      <div>
        <h1>{page.heading}</h1>
        <p>{page.intro}</p>
      </div>
    </section>
  );
}

export function EditorialTable({ hero = false }: { hero?: boolean }) {
  return (
    <figure className={hero ? "editorial-hero-photo" : "editorial-table-photo"}>
      {/* Prebuilt sizes keep the main photograph independent of cold image resizing. */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/images/live/editorial-table-1280.webp"
        srcSet="/images/live/editorial-table-480.webp 480w, /images/live/editorial-table-768.webp 768w, /images/live/editorial-table-1280.webp 1280w, /images/live/editorial-table-1536.webp 1536w"
        sizes={
          hero
            ? "(max-width: 767px) 100vw, 94vw"
            : "(max-width: 767px) 92vw, 50vw"
        }
        width={1536}
        height={1024}
        alt="Representative illustration of four chicken pakodi flavours on a table"
        fetchPriority={hero ? "high" : undefined}
        loading={hero ? "eager" : "lazy"}
        decoding="async"
      />
      <figcaption>
        Four flavours of Patnam Pakodi. Food illustration; presentation may
        vary.
      </figcaption>
    </figure>
  );
}

export function FoodPortrait({ image, alt }: { image: string; alt: string }) {
  return (
    <figure className="editorial-food-portrait">
      <Image
        src={image}
        alt={alt}
        width={1024}
        height={1024}
        sizes="(max-width: 767px) 92vw, 45vw"
      />
      <figcaption>Representative food illustration.</figcaption>
    </figure>
  );
}

export function BranchCard({
  outlet,
  detail = false,
}: {
  outlet: Outlet;
  detail?: boolean;
}) {
  const query = outlet.address || `Patnam Pakodi ${outlet.name} ${outlet.city}`;
  return (
    <article className="editorial-branch-card">
      <div className="branch-heading">
        <Icon name="pin" />
        <h2>Patnam Pakodi, {outlet.name}</h2>
      </div>
      <p className="branch-current">Our only serving branch</p>
      <dl className="branch-facts">
        <div>
          <dt>Find us</dt>
          <dd>{outlet.address || `${outlet.name}, ${outlet.city}`}</dd>
        </div>
        <div>
          <dt>Listed opening hours</dt>
          <dd>{outlet.hours || "Please call the team for current hours."}</dd>
        </div>
        {outlet.phone && (
          <div>
            <dt>Branch phone</dt>
            <dd>
              <a href={`tel:${outlet.phone}`}>{outlet.phone}</a>
            </dd>
          </div>
        )}
      </dl>
      <p className="editorial-note">
        Address, hours and branch phone follow our current website listing.
        Please call to confirm before travelling.
      </p>
      <div className="actions">
        <a
          className="button"
          href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`}
          target="_blank"
          rel="noreferrer"
        >
          {detail ? "Open outlet map" : "Look up on Google Maps"}
          <Icon name="arrow" />
          <span className="sr-only">(opens a new tab)</span>
        </a>
        {!detail && (
          <SiteLink className="text-link" href={`/branches/${outlet.slug}/`}>
            Branch details <Icon name="arrow" />
          </SiteLink>
        )}
      </div>
    </article>
  );
}

export function VisitInvitation({ content }: { content: Storefront }) {
  const outlet = content.outlets.find((item) => item.slug === "kukatpally");
  return (
    <section className="editorial-visit-band">
      <div className="container editorial-visit-inner">
        <div>
          <h2>
            A little closer.
            <br />
            In Kukatpally.
          </h2>
          <p>
            Make your next snack break a Patnam one. We are currently serving
            only in Kukatpally, Hyderabad.
          </p>
          <SiteLink href="/branches/" className="text-link">
            Plan your visit <Icon name="arrow" />
          </SiteLink>
        </div>
        <div className="editorial-visit-details">
          <h3>
            Come for the pakodi.
            <br />
            Stay for the conversation.
          </h3>
          {outlet?.address && <p>{outlet.address}</p>}
          {outlet?.phone && (
            <a className="text-link" href={`tel:${outlet.phone}`}>
              Call the Kukatpally branch <Icon name="phone" />
            </a>
          )}
          <p className="editorial-note">
            Please call ahead for current hours and availability.
          </p>
        </div>
      </div>
    </section>
  );
}

export function FranchiseInvitation() {
  return (
    <EnquiryProvider>
      <section className="container editorial-section editorial-franchise-invite">
        <div>
          <h2>
            Good flavour.
            <br />A new beginning.
          </h2>
          <p>
            From a compact cart to a shop of your own, explore four ways to
            bring Patnam Pakodi to your neighbourhood.
          </p>
        </div>
        <div className="editorial-invite-actions">
          <SiteLink href="/franchise/" className="button">
            Explore franchise formats <Icon name="arrow" />
          </SiteLink>
          <button className="text-link" data-enquiry="Download Brochure">
            Download brochure
          </button>
          <noscript>
            <a href="/api/v1/brochure/" download="patnam-pakodi-brochure.pdf">
              Download the PDF brochure
            </a>
          </noscript>
        </div>
      </section>
    </EnquiryProvider>
  );
}
