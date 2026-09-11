import Image from "next/image";
import { notFound } from "next/navigation";
import { getStorefront } from "@/lib/content";
import { getCatalog } from "@/lib/catalog";
import { pageMetadata } from "@/lib/seo";
import { SiteLink } from "@/components/SiteLink";
import { Icon } from "@/components/Icon";
import { ProductCard } from "@/components/ProductCard";
import { JsonLd } from "@/components/JsonLd";
import { EnquiryProvider } from "@/components/QuickEnquiry";
import type { Schema } from "@/lib/commerce";
export const dynamic = "force-dynamic";
export async function generateMetadata() {
  const content = await getStorefront(),
    page = content.pages.find((item) => item.slug === "home");
  return page
    ? pageMetadata({
        ...page,
        title: "Patnam Pakodi | Fresh Pakodi & Ready Mixes",
        description:
          "Explore Patnam Pakodi fresh food and ready mixes. Discover the menu, check delivery availability, shop your favourites and find a branch near you.",
      })
    : {};
}
const flavourImages: Record<string, string> = {
  "pachi-mirchi-chicken-pakodi": "/images/live/822655cabe9a63a6.webp",
  "kothimeera-chicken-pakodi": "/images/live/1d5b2efa231d50d8.webp",
  "kaju-chicken-pakodi": "/images/live/672607b47463342a.webp",
};
export default async function Home() {
  const [content, catalog] = await Promise.all([getStorefront(), getCatalog()]);
  const page = content.pages.find((item) => item.slug === "home");
  if (!page) notFound();
  const fresh = catalog
    .filter((item) => item.product.mode === "fresh")
    .slice(0, 4);
  const packaged = catalog
    .filter((item) => item.product.mode === "packaged")
    .slice(0, 4);
  const faqs: Schema["ContentBlock"][] = [];
  const visit = (blocks: Schema["ContentBlock"][]) => {
    for (const block of blocks) {
      if (block.kind === "faq") faqs.push(block);
      visit(block.children);
    }
  };
  visit(page.blocks);
  const copy = (title: string, fallback: string) =>
    page.sections.find((section) => section.title === title)?.body ?? fallback;
  return (
    <>
      <JsonLd
        value={{
          "@context": "https://schema.org",
          "@type": "Organization",
          name: content.brand,
          url: "https://patnampakodi.com",
        }}
      />
      <section className="container store-hero">
        <div className="store-hero-copy">
          <h1>
            {page.heading}
            <span>
              Made for
              <br />
              one more bite.
            </span>
          </h1>
          <p>
            {copy(
              "Shopping introduction",
              "Fresh pakodi for today. Ready mixes for your kitchen. Find your flavour, your way.",
            )}
          </p>
          <div className="hero-shopping-actions">
            <SiteLink className="button" href="/menu/">
              <Icon name="fresh" />
              Order fresh
              <Icon name="arrow" />
            </SiteLink>
            <SiteLink className="button button-outline" href="/shop/">
              <Icon name="box" />
              Shop packaged
            </SiteLink>
          </div>
          <p className="hero-footnote">
            <Icon name="pin" />
            Check your PIN code for delivery availability.
          </p>
        </div>
        <div className="store-hero-image">
          {/* Build-generated responsive artwork avoids a cold image resize. */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/generated/hero-22b33848ef67e688-768.webp"
            srcSet="/generated/hero-22b33848ef67e688-384.webp 384w, /generated/hero-22b33848ef67e688-768.webp 768w, /generated/hero-22b33848ef67e688-1024.webp 1024w"
            alt="Patnam Pakodi chicken pakodi with curry leaves and lemon"
            width={1024}
            height={768}
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
      <div className="store-benefits">
        <div className="container">
          <div>
            <Icon name="fresh" />
            <span>Fresh from the kitchen</span>
          </div>
          <div>
            <Icon name="box" />
            <span>Flavour to take home</span>
          </div>
          <div>
            <Icon name="shield" />
            <span>Secure online payment</span>
          </div>
          <div>
            <Icon name="heart" />
            <span>Save your favourites</span>
          </div>
        </div>
      </div>
      <section className="container store-section">
        <div className="store-section-heading">
          <div>
            <h2>What are you craving?</h2>
            <p>A little something for every kind of hunger.</p>
          </div>
          <SiteLink className="text-link" href="/menu/">
            Explore the menu
            <Icon name="arrow" />
          </SiteLink>
        </div>
        <div className="category-discovery">
          {[
            {
              title: "Fresh pakodi",
              text: "For the love of crunch",
              image: "/images/live/96a8865cb1117019.webp",
              href: "/menu/?category=Dry",
            },
            {
              title: "Ready mixes",
              text: "Your kitchen, our flavours",
              image: "/images/live/green-chilli-pakodi-ready-mix.webp",
              href: "/shop/",
            },
            {
              title: "Your local Patnam",
              text: "Find a branch near you",
              image: "/images/live/4acae447c22f17a3.webp",
              href: "/branches/",
            },
          ].map((item) => (
            <SiteLink
              href={item.href}
              className="category-discovery-card"
              key={item.title}
            >
              <Image
                src={item.image}
                alt=""
                width={400}
                height={320}
                sizes="(max-width: 600px) 80vw, 30vw"
              />
              <div>
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </div>
              <Icon name="arrow" />
            </SiteLink>
          ))}
        </div>
      </section>
      <section className="container store-section">
        <div className="store-section-heading">
          <div>
            <h2>Hot. Crisp. Hard to share.</h2>
            <p>
              {copy(
                "Fresh selection",
                "Bring a little spice to your next snack break.",
              )}
            </p>
          </div>
          <SiteLink className="text-link" href="/menu/">
            See the fresh menu
            <Icon name="arrow" />
          </SiteLink>
        </div>
        {fresh.length ? (
          <div className="store-product-grid home-products">
            {fresh.map((item) => (
              <ProductCard key={item.id} item={item} />
            ))}
          </div>
        ) : (
          <div className="food-editorial-grid">
            {content.menu
              .filter((item) => Object.hasOwn(flavourImages, item.slug))
              .map((item) => (
                <article key={item.slug}>
                  <Image
                    src={flavourImages[item.slug]}
                    alt={item.name}
                    width={500}
                    height={500}
                    sizes="(max-width: 600px) 90vw, 30vw"
                  />
                  <h3>{item.name}</h3>
                  <p>{item.description}</p>
                  <SiteLink href="/menu/" className="text-link">
                    Explore the menu
                    <Icon name="arrow" />
                  </SiteLink>
                </article>
              ))}
          </div>
        )}
      </section>
      <section className="packaged-feature">
        <div className="container">
          <div className="store-section-heading">
            <div>
              <h2>Your kitchen. Our kind of flavour.</h2>
              <p>
                {copy(
                  "Packaged selection",
                  "Keep a little Patnam Pakodi in your pantry with our ready-mix range.",
                )}
              </p>
            </div>
            <SiteLink className="text-link" href="/shop/">
              Explore ready mixes
              <Icon name="arrow" />
            </SiteLink>
          </div>
          {packaged.length ? (
            <div className="store-product-grid home-products">
              {packaged.map((item) => (
                <ProductCard key={item.id} item={item} />
              ))}
            </div>
          ) : (
            <div className="packaged-editorial">
              {[
                ["Green chilli", "green-chilli"],
                ["Chettinadu", "chettinadu"],
                ["Pepper", "pepper"],
                ["Red chilli", "red-chilli"],
              ].map(([name, file]) => (
                <SiteLink href="/shop/" key={file}>
                  <Image
                    src={`/images/live/${file}-pakodi-ready-mix.webp`}
                    width={450}
                    height={360}
                    sizes="(max-width: 600px) 45vw, 22vw"
                    alt={`${name} Pakodi Ready Mix packaging`}
                  />
                  <h3>{name}</h3>
                  <span>
                    Explore the range <Icon name="arrow" />
                  </span>
                </SiteLink>
              ))}
            </div>
          )}
        </div>
      </section>
      <section className="container store-section how-to-order">
        <div>
          <h2>
            Good food.
            <br />A few easy steps.
          </h2>
          <p>Fresh from a nearby kitchen or ready to make at home.</p>
        </div>
        <ol>
          <li>
            <Icon name="pin" />
            <div>
              <h3>Choose your way</h3>
              <p>
                Pick fresh food or packaged products and check your delivery
                PIN.
              </p>
            </div>
          </li>
          <li>
            <Icon name="bag" />
            <div>
              <h3>Find your favourites</h3>
              <p>
                Add your picks and review the full total, including delivery.
              </p>
            </div>
          </li>
          <li>
            <Icon name="truck" />
            <div>
              <h3>We’ll take it from here</h3>
              <p>
                Pay securely and follow your order through your private link.
              </p>
            </div>
          </li>
        </ol>
      </section>
      <section className="container store-section store-story">
        <Image
          src="/images/live/e475923ba3b97617.webp"
          alt="The Patnam Pakodi kitchen"
          width={640}
          height={640}
          sizes="(max-width: 767px) 92vw, 45vw"
        />
        <div>
          <h2>
            A little spice belongs
            <br />
            in every day.
          </h2>
          <p>
            {copy(
              "Shopping story",
              "Some moments call for good company and something crisp to share. Get to know the story behind Patnam Pakodi, our food and our growing family of outlets.",
            )}
          </p>
          <SiteLink href="/about-us/" className="text-link">
            Our story
            <Icon name="arrow" />
          </SiteLink>
          <div className="story-outlet-link">
            <Icon name="pin" />
            <div>
              <h3>Come hungry. Leave happy.</h3>
              <SiteLink href="/branches/">
                Find your nearest branch
                <Icon name="arrow" />
              </SiteLink>
            </div>
          </div>
        </div>
      </section>
      <EnquiryProvider>
        <section className="container franchise-invitation">
          <div>
            <h2>Make room for your next big idea.</h2>
            <p>Explore the Patnam Pakodi franchise opportunity.</p>
          </div>
          <div className="actions">
            <SiteLink href="/franchise/" className="button button-outline">
              Explore franchise
              <Icon name="arrow" />
            </SiteLink>
            <button className="text-link" data-enquiry="Download Brochure">
              Download brochure
            </button>
          </div>
        </section>
      </EnquiryProvider>
      {faqs.length > 0 && (
        <section className="container store-section home-faq">
          <div>
            <h2>A few things you might be wondering.</h2>
            <p>Have something else in mind?</p>
            <SiteLink href="/contact/" className="text-link">
              Talk to our team
              <Icon name="arrow" />
            </SiteLink>
          </div>
          <div>
            {faqs.slice(0, 5).map((faq, index) => (
              <details key={index}>
                <summary>
                  {faq.title}
                  <Icon name="plus" />
                </summary>
                <p>{faq.text}</p>
              </details>
            ))}
          </div>
        </section>
      )}
    </>
  );
}
