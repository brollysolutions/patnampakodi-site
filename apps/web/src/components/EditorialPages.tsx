import type { PageContent, Storefront } from "@/lib/content";
import { SiteLink } from "./SiteLink";
import { Icon } from "./Icon";
import { MenuGrid } from "./MenuGrid";
import { FranchiseForm } from "./FranchiseForm";
import { EnquiryProvider } from "./QuickEnquiry";
import {
  BranchCard,
  EditorialTable,
  FoodPortrait,
  FranchiseInvitation,
  Paragraphs,
  VisitInvitation,
} from "./Editorial";
import { money } from "@/lib/commerce";

type Props = { page: PageContent; content: Storefront };

export function MenuEditorial({ page, content }: Props) {
  return (
    <>
      <section
        className="container editorial-menu"
        aria-label="Our four signature flavours"
      >
        <MenuGrid items={content.menu} headingLevel={2} expanded />
        <div className="menu-visit-note">
          <p>
            All four flavours are chicken pakodi. Images are representative
            illustrations, not verified photographs of each flavour. Please ask
            our team about ingredients, allergens and serving details.
          </p>
          <SiteLink className="button" href="/branches/">
            Visit Kukatpally <Icon name="arrow" />
          </SiteLink>
        </div>
      </section>
      <section className="container editorial-section editorial-reading-pair">
        {page.sections.map((section) => (
          <div key={section.title}>
            <h2>{section.title}</h2>
            <Paragraphs text={section.body} />
          </div>
        ))}
      </section>
      <VisitInvitation content={content} />
    </>
  );
}

export function StoryEditorial({ page, content }: Props) {
  return (
    <>
      <section className="container editorial-section editorial-story-opening">
        <FoodPortrait
          image="/images/live/signature-pachi-mirchi.webp"
          alt="Representative illustration of green chilli chicken pakodi"
        />
        <div className="editorial-prose">
          {page.sections.slice(0, 1).map((section) => (
            <div key={section.title}>
              <h2>{section.title}</h2>
              <Paragraphs text={section.body} />
            </div>
          ))}
          <p className="editorial-brand-line">Life Lo Spice Undali.</p>
        </div>
      </section>
      <section className="editorial-story-statement">
        <div className="container">
          <p>
            Red chilli. Green chilli.
            <br />
            Pepper. Chettinad.
            <br />A little spice, your way.
          </p>
          <SiteLink href="/menu/" className="text-link">
            Get to know the four flavours <Icon name="arrow" />
          </SiteLink>
        </div>
      </section>
      <section className="container editorial-section editorial-story-chapters">
        {page.sections.slice(1).map((section) => (
          <article key={section.title}>
            <h2>{section.title}</h2>
            <div>
              <Paragraphs text={section.body} />
            </div>
          </article>
        ))}
      </section>
      <VisitInvitation content={content} />
      <FranchiseInvitation />
    </>
  );
}

export function BranchesEditorial({ page, content }: Props) {
  const outlet = content.outlets.find((item) => item.slug === "kukatpally");
  return (
    <>
      <section className="container editorial-section editorial-branch-layout">
        <div className="outlet-grid">
          {outlet ? (
            <BranchCard outlet={outlet} />
          ) : (
            <p>
              Please contact our team for current Kukatpally branch details.
            </p>
          )}
        </div>
        <div className="editorial-prose">
          {page.sections.map((section) => (
            <section key={section.title}>
              <h2>{section.title}</h2>
              <Paragraphs text={section.body} />
            </section>
          ))}
          <SiteLink href="/menu/" className="text-link">
            Explore our four flavours <Icon name="arrow" />
          </SiteLink>
        </div>
      </section>
      <section className="container editorial-location-story">
        <EditorialTable />
        <div>
          <h2>
            Your neighbourhood.
            <br />
            Our kind of flavour.
          </h2>
          <p>
            Some moments call for a pause, good company and something crisp to
            share. Find your flavour at Patnam Pakodi, Kukatpally.
          </p>
          <SiteLink href="/about-us/" className="text-link">
            Read our story <Icon name="arrow" />
          </SiteLink>
        </div>
      </section>
      <FranchiseInvitation />
    </>
  );
}

export function FranchiseEditorial({ page, content }: Props) {
  const formats = page.blocks.filter((block) => block.kind === "group");
  return (
    <>
      <section className="container editorial-section franchise-models">
        <div className="editorial-section-heading">
          <h2>
            Four formats.
            <br />
            Room for your ambition.
          </h2>
          <p>
            Compare the setup that suits your space. These package details come
            from our franchise brochure; our team can help you work through the
            specifics.
          </p>
        </div>
        <div className="signature-models editorial-formats">
          {content.franchise_models.map((model) => (
            <article key={model.image}>
              <div>
                <h3>{model.name}</h3>
                {model.investment_paise != null && (
                  <p className="franchise-price">
                    {money(model.investment_paise)}
                  </p>
                )}
                <p>
                  {formats.find((block) => block.record_slug === model.image)
                    ?.text || model.description}
                </p>
              </div>
              <ul>
                {formats
                  .find((block) => block.record_slug === model.image)
                  ?.items.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
              </ul>
            </article>
          ))}
        </div>
        <p className="editorial-note">
          Brochure package prices. Customized inclusions may change the price.
          Ask for a current written breakdown for your location and format.
        </p>
      </section>
      <section className="editorial-franchise-process">
        <div className="container editorial-section">
          <div className="editorial-section-heading">
            <h2>
              From an idea
              <br />
              to a conversation.
            </h2>
            <p>
              Start by exploring the formats, then bring your location and
              questions to our team.
            </p>
          </div>
          <ol className="editorial-steps">
            <li>
              <h3>Explore your format</h3>
              <p>
                Read the package comparison and brochure. Think about your
                space, setup and the kind of outlet you want to run.
              </p>
            </li>
            <li>
              <h3>Discuss your location</h3>
              <p>
                Share your proposed area and available space. Talk through
                location suitability, equipment, training and operating
                responsibilities.
              </p>
            </li>
            <li>
              <h3>Confirm your next steps</h3>
              <p>
                Request the current inclusions, cost breakdown and terms in
                writing before committing to a setup or launch schedule.
              </p>
            </li>
          </ol>
        </div>
      </section>
      <section className="container editorial-section franchise-inclusions">
        <div className="editorial-section-heading">
          <h2>
            The detail
            <br />
            behind the setup.
          </h2>
          <p>
            Equipment, preparation tools and brand materials, explained by
            format.
          </p>
        </div>
        {page.sections.map((section) => (
          <details open key={section.title}>
            <summary>
              {section.title}
              <span aria-hidden="true" className="faq-indicator" />
            </summary>
            <p>{section.body}</p>
          </details>
        ))}
        <p className="editorial-note">
          The brochure describes equipment for broader food setups. Our current
          customer menu contains only the four signature chicken pakodi
          flavours. Discuss the menu and exact equipment for your proposed
          franchise with our team.
        </p>
        <EnquiryProvider>
          <button
            className="button button-outline"
            data-enquiry="Download Brochure"
          >
            Download brochure <Icon name="arrow" />
          </button>
          <noscript>
            <a href="/api/v1/brochure/" download="patnam-pakodi-brochure.pdf">
              Download the PDF brochure
            </a>
          </noscript>
        </EnquiryProvider>
      </section>
      <section className="container editorial-section editorial-franchise-brief">
        <h2>
          Bring these questions
          <br />
          to the table.
        </h2>
        <div>
          <p>
            A clear conversation helps you compare your options. Alongside the
            brochure package, discuss:
          </p>
          <ul>
            <li>Your location, available space and approval process.</li>
            <li>Training, staffing and daily preparation procedures.</li>
            <li>Food-licence arrangements and the exact setup inclusions.</li>
            <li>
              Ongoing supplies, operating costs, royalty and territory terms.
            </li>
            <li>
              A realistic launch schedule and responsibilities on both sides.
            </li>
          </ul>
        </div>
      </section>
      <section className="container editorial-section franchise-enquiry-layout">
        <div>
          <h2>
            Tell us what
            <br />
            you have in mind.
          </h2>
          <p>
            Share your proposed location and the format that interests you. Our
            franchise team can help you explore the details.
          </p>
          {content.contact_phone && (
            <a className="text-link" href={`tel:${content.contact_phone}`}>
              Call our franchise team <Icon name="phone" />
            </a>
          )}
          <p className="editorial-note">
            Want to try the food first? Our only serving branch is currently
            Kukatpally.
          </p>
          <SiteLink href="/branches/" className="text-link">
            Plan a Kukatpally visit <Icon name="arrow" />
          </SiteLink>
        </div>
        <FranchiseForm />
      </section>
    </>
  );
}

export function ContactEditorial({ page, content }: Props) {
  const outlet = content.outlets.find((item) => item.slug === "kukatpally");
  return (
    <>
      <section className="container editorial-section editorial-contact-layout">
        <div className="editorial-contact-main">
          <h2>Central & franchise enquiries</h2>
          <p>
            For franchise opportunities, brand information and general
            questions.
          </p>
          {content.contact_phone && (
            <a
              className="editorial-phone"
              href={`tel:${content.contact_phone}`}
            >
              {content.contact_phone}
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
          <div className="actions">
            {content.contact_phone && (
              <a
                className="button"
                href={`https://wa.me/${content.contact_phone.replace("+", "")}`}
                target="_blank"
                rel="noreferrer"
              >
                Contact on WhatsApp <Icon name="arrow" />
                <span className="sr-only">(opens a new tab)</span>
              </a>
            )}
            <a
              className="text-link"
              href="https://www.instagram.com/patnampakodi/"
              target="_blank"
              rel="noreferrer"
            >
              Instagram: @patnampakodi
              <span className="sr-only"> (opens a new tab)</span>
            </a>
          </div>
        </div>
        <div className="editorial-prose">
          {page.sections.map((section) => (
            <section key={section.title}>
              <h2>{section.title}</h2>
              <Paragraphs text={section.body} />
            </section>
          ))}
          <SiteLink className="text-link" href="/branches/">
            Kukatpally branch details <Icon name="arrow" />
          </SiteLink>
        </div>
      </section>
      <section className="editorial-contact-topics">
        <div className="container editorial-section">
          <h2>How can we help?</h2>
          <div>
            {page.blocks
              .filter((block) => block.kind === "group")
              .map((block) => (
                <article key={block.title}>
                  <h3>{block.title}</h3>
                  <p>{block.text}</p>
                </article>
              ))}
          </div>
        </div>
      </section>
      <section className="container editorial-section editorial-contact-visit">
        <div>
          <h2>
            For a pakodi break,
            <br />
            head to Kukatpally.
          </h2>
          <p>
            Our branch team can help with today’s flavours and practical details
            for your visit.
          </p>
          <SiteLink href="/menu/" className="text-link">
            Get to know the menu <Icon name="arrow" />
          </SiteLink>
        </div>
        {outlet && <BranchCard outlet={outlet} />}
      </section>
      <FranchiseInvitation />
    </>
  );
}
