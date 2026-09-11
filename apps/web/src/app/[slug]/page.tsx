import Image from "next/image";
import { CatalogBrowser } from "@/components/CatalogBrowser";
import { getCatalog } from "@/lib/catalog";
import { StructuredPage } from "@/components/StructuredPage";
import { ReferenceDiscovery } from "@/components/ReferenceDiscovery";
import { notFound } from "next/navigation";
import { HeroImage } from "@/components/HeroImage";
import { SiteLink } from "@/components/SiteLink";
import { JsonLd } from "@/components/JsonLd";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
import {
  filterMenu,
  filterOutlets,
  PUBLIC_SLUGS,
  SITE_URL,
  pathFor,
} from "@/lib/policy.mjs";

export const dynamic = "force-dynamic";
type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  if (!PUBLIC_SLUGS.includes(slug) || slug === "home")
    return { robots: { index: false, follow: false } };
  const content = await getStorefront();
  const page = content.pages.find((item) => item.slug === slug);
  return page
    ? pageMetadata(page)
    : { robots: { index: false, follow: false } };
}

export default async function PublicPage({ params, searchParams }: Props) {
  const { slug } = await params;
  if (!PUBLIC_SLUGS.includes(slug) || slug === "home") notFound();
  const content = await getStorefront();
  const page = content.pages.find((item) => item.slug === slug);
  if (!page) notFound();
  if (page.blocks.length && !["menu", "branches"].includes(slug))
    return <StructuredPage blocks={page.blocks} slug={slug} />;
  const query = await searchParams;
  if (slug === "menu" && (await getCatalog({ mode: "fresh" })).length)
    return (
      <CatalogBrowser
        query={{
          ...query,
          category:
            typeof query.category === "string"
              ? query.category.toLowerCase()
              : undefined,
        }}
        mode="fresh"
      />
    );
  const FranchiseForm =
    slug === "franchise"
      ? (await import("@/components/FranchiseForm")).FranchiseForm
      : null;
  const q = typeof query.q === "string" ? query.q.slice(0, 100) : "";
  const category = typeof query.category === "string" ? query.category : "";
  if (page.blocks.length && ["menu", "branches"].includes(slug))
    return (
      <ReferenceDiscovery
        blocks={page.blocks}
        slug={slug}
        q={q}
        category={category}
        outlets={content.outlets}
        items={content.menu}
      />
    );
  const menu = filterMenu(content.menu, category, q) as typeof content.menu;
  const outlets = filterOutlets(content.outlets, q) as typeof content.outlets;
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
      <section
        className={`container page-intro ${slug === "about-us" ? "about-intro" : ""}`}
      >
        <div>
          <SiteLink href="/" className="breadcrumb">
            Home <span aria-hidden="true">/</span>
          </SiteLink>
          <h1>{page.heading}</h1>
          <p>{page.intro}</p>
        </div>
        {slug === "about-us" && <HeroImage priority />}
      </section>
      {slug === "menu" && (
        <section className="container menu-section" aria-label="Our menu">
          <form method="get" action="/menu/" className="filter-form">
            <div className="search-field">
              <label htmlFor="menu-search">Find your favourite</label>
              <div>
                <input
                  id="menu-search"
                  name="q"
                  type="search"
                  defaultValue={q}
                  maxLength={100}
                  placeholder="Try chicken, mirchi, or a cool drink"
                />
                <button className="button button-small" type="submit">
                  Search <span aria-hidden="true">→</span>
                </button>
              </div>
            </div>
            <fieldset className="category-tabs">
              <legend className="sr-only">Menu category</legend>
              {["", "Dry", "Wet", "Bowls", "Dips", "Drinks"].map((value) => (
                <button
                  key={value}
                  type="submit"
                  name="category"
                  value={value}
                  aria-pressed={category === value}
                >
                  {value || "All the good stuff"}
                </button>
              ))}
            </fieldset>
          </form>
          <div className="results-line">
            <p>
              {menu.length} {menu.length === 1 ? "item" : "items"}
              {category ? ` · ${category}` : " on the menu"}
            </p>
            {(q || category) && (
              <SiteLink href="/menu/">Clear filters</SiteLink>
            )}
          </div>
          {menu.length ? (
            <div className="menu-grid">
              {menu.map((item) => (
                <article className="menu-item" key={item.slug}>
                  <div>
                    <span className="menu-category">
                      {item.category === "Dry"
                        ? "The crunch collection"
                        : item.category}
                    </span>
                    <h2>{item.name}</h2>
                    {item.description && <p>{item.description}</p>}
                    <span className="dietary">
                      {item.dietary === "non-veg" ? (
                        <>
                          <i aria-hidden="true" /> Non-vegetarian
                        </>
                      ) : item.dietary === "veg" ? (
                        "Vegetarian"
                      ) : (
                        "Dietary information: ask in store"
                      )}
                    </span>
                  </div>
                  <span className="menu-price">
                    {item.price_paise == null
                      ? "Ask in store"
                      : new Intl.NumberFormat("en-IN", {
                          style: "currency",
                          currency: "INR",
                        }).format(item.price_paise / 100)}
                  </span>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <h2>No bites found.</h2>
              <p>Try another name or browse the full menu.</p>
              <SiteLink className="button" href="/menu/">
                Show the full menu
              </SiteLink>
            </div>
          )}
          <aside className="food-note">
            <span aria-hidden="true">ⓘ</span>
            <p>
              Prices and availability are confirmed in store. Please ask the
              team about ingredients and allergens before ordering.
            </p>
          </aside>
        </section>
      )}
      {slug === "branches" && (
        <section className="container section locator">
          <form method="get" action="/branches/" className="filter-form">
            <div className="search-field">
              <label htmlFor="outlet-search">
                City, neighbourhood or pincode
              </label>
              <div>
                <input
                  id="outlet-search"
                  name="q"
                  type="search"
                  defaultValue={q}
                  maxLength={100}
                  placeholder="Try Hyderabad or Kukatpally"
                />
                <button type="submit" className="button button-small">
                  Find a store <span aria-hidden="true">→</span>
                </button>
              </div>
            </div>
          </form>
          <div className="results-line">
            <p>
              {outlets.length} {outlets.length === 1 ? "location" : "locations"}
            </p>
            {q && <SiteLink href="/branches/">Clear search</SiteLink>}
          </div>
          <div className="outlet-grid">
            {outlets.map((outlet) => (
              <article key={outlet.slug}>
                <span className="location-icon" aria-hidden="true">
                  ↗
                </span>
                <h2>{outlet.name}</h2>
                <a href={`/branches/${outlet.slug}/`}>Outlet details</a>
                <p>
                  {outlet.city} · {outlet.pincode}
                </p>
                {outlet.address && <p>{outlet.address}</p>}
                {outlet.hours && <p>{outlet.hours}</p>}
                <a
                  className="text-link"
                  href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`Patnam Pakodi ${outlet.name} ${outlet.city}`)}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Look up on Google Maps{" "}
                  <span className="sr-only">(opens a new tab)</span>
                  <span aria-hidden="true">↗</span>
                </a>
              </article>
            ))}
          </div>
          {outlets.length === 0 && (
            <div className="empty-state">
              <h2>Let’s try another neighbourhood.</h2>
              <p>No locations match that search.</p>
              <SiteLink className="button" href="/branches/">
                Show all locations
              </SiteLink>
            </div>
          )}
          <aside className="food-note">
            <p>
              Check the current address and opening hours on the outlet’s map
              listing before you travel.
            </p>
          </aside>
        </section>
      )}
      {slug === "shop" && (
        <section className="container section shop-intro">
          <div className="type-art" aria-hidden="true">
            A little spice.
            <br />
            <span>At your place.</span>
            <span className="art-star">✳</span>
          </div>
          <div>
            <h2>{page.sections[0]?.title}</h2>
            <p>{page.sections[0]?.body}</p>
            <SiteLink className="button" href="/menu/">
              Explore the menu <span aria-hidden="true">↗</span>
            </SiteLink>
          </div>
        </section>
      )}
      {slug === "franchise" && (
        <>
          <section className="container section">
            {FranchiseForm && <FranchiseForm />}
          </section>
          <section className="container section franchise-models">
            <div className="section-heading">
              <h2>
                Four ways to
                <br />
                make it yours.
              </h2>
              <p>
                Start with the format.
                <br />
                Talk through the details with our team.
              </p>
            </div>
            <div className="model-grid">
              {content.franchise_models.map((model) => (
                <article key={model.name}>
                  <div className="model-image">
                    <Image
                      src={`/images/franchise-${model.image}.png`}
                      width={768}
                      height={1024}
                      alt={`${model.name} as shown on the existing Patnam Pakodi website`}
                      sizes="(max-width: 700px) 44vw, (max-width: 1100px) 45vw, 290px"
                    />
                  </div>
                  <h3>{model.name}</h3>
                  <p>{model.description}</p>
                  <SiteLink className="text-link" href="/contact/">
                    Discuss this format <span aria-hidden="true">↗</span>
                  </SiteLink>
                </article>
              ))}
            </div>
            <p className="model-note">
              Request the current investment, inclusions, royalty terms and
              location requirements directly from the franchise team.
            </p>
          </section>
          <section className="story-band">
            <div className="container story-grid">
              <h2>{page.sections[0]?.title}</h2>
              <div>
                <p>{page.sections[0]?.body}</p>
                <SiteLink className="button button-primary" href="/contact/">
                  Start a conversation <span aria-hidden="true">↗</span>
                </SiteLink>
              </div>
            </div>
          </section>
        </>
      )}
      {slug === "about-us" && (
        <section className="container section prose-sections">
          {page.sections.map((section) => (
            <section key={section.title}>
              <h2>{section.title}</h2>
              <p>{section.body}</p>
            </section>
          ))}
          <SiteLink className="button button-primary" href="/menu/">
            Find your favourite <span aria-hidden="true">↗</span>
          </SiteLink>
        </section>
      )}
      {slug === "contact" && (
        <section className="container section contact-grid">
          <div className="contact-card">
            <h2>
              A good conversation
              <br />
              starts here.
            </h2>
            <p>For franchise opportunities, menu questions or a hello.</p>
            {content.contact_email ? (
              <a
                className="contact-email"
                href={`mailto:${content.contact_email}`}
              >
                {content.contact_email} <span aria-hidden="true">↗</span>
              </a>
            ) : (
              <p>Contact details will be available shortly.</p>
            )}
            <p className="small">
              Your email app opens when you select the address.
            </p>
          </div>
          <div className="contact-directions">
            <h2>Looking for a snack?</h2>
            <p>
              Browse our locations and look up your nearest Patnam Pakodi on the
              map.
            </p>
            <SiteLink className="button" href="/branches/">
              Find a store <span aria-hidden="true">↗</span>
            </SiteLink>
          </div>
        </section>
      )}
    </>
  );
}
