import { SiteLink } from "./SiteLink";
import { getStorefront } from "@/lib/content";
import Image from "next/image";
import { StructuredPage } from "./StructuredPage";

const links = [
  ["Home", "/"],
  ["About Us", "/about-us/"],
  ["Menu", "/menu/"],
  ["Branches", "/branches/"],
  ["Franchise", "/franchise/"],
  ["Recipe", "/shop/"],
  ["Contact", "/contact/"],
] as const;

const mobileLinks = [...links, ["Cart", "/cart/"]] as const;

export function Wordmark() {
  return (
    <SiteLink className="wordmark" href="/" aria-label="Patnam Pakodi home">
      <Image
        className="reference-logo"
        src="/images/live/656da99ddfd65b8a.webp"
        alt="Patnam Pakodi"
        width={377}
        height={366}
        priority
      />
    </SiteLink>
  );
}

export function Header() {
  return (
    <header className="site-header">
      <div className="container header-inner">
        <Wordmark />
        <nav aria-label="Main navigation" className="desktop-nav">
          {links.map(([name, href]) => (
            <SiteLink href={href} key={href}>
              {name}
            </SiteLink>
          ))}
        </nav>
        <a
          className="button button-small header-franchise"
          href="https://wa.me/919000366219"
        >
          WhatsApp Us
        </a>
        <details className="mobile-nav">
          <summary>
            Menu <span aria-hidden="true">＋</span>
          </summary>
          <nav aria-label="Mobile navigation">
            {mobileLinks.map(([name, href]) => (
              <SiteLink href={href} key={href}>
                {name}
              </SiteLink>
            ))}
          </nav>
        </details>
      </div>
    </header>
  );
}

export async function Footer() {
  const content = await getStorefront().catch(() => null);
  const footer = content?.pages.find((page) => page.slug === "site-footer");
  if (footer?.blocks.length)
    return (
      <footer>
        <StructuredPage blocks={footer.blocks} slug="footer" />
        <nav
          className="container footer-bottom"
          aria-label="Orders and policies"
        >
          <SiteLink href="/cart/">Cart</SiteLink>
          <SiteLink href="/track/">Track your order</SiteLink>
          {content?.pages
            .filter((page) => page.slug.startsWith("policies/"))
            .map((page) => (
              <a key={page.slug} href={`/${page.slug}/`}>
                {page.heading}
              </a>
            ))}
        </nav>
      </footer>
    );
  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <div>
          <Wordmark />
          <p>Life Lo Spice Undali.</p>
        </div>
        <nav aria-label="Explore">
          <p className="footer-label">Come hungry.</p>
          <SiteLink href="/menu/">Explore the menu</SiteLink>
          <SiteLink href="/branches/">Find a store</SiteLink>
          <SiteLink href="/shop/">Shop ready-mixes</SiteLink>
          <SiteLink href="/track/">Track your order</SiteLink>
        </nav>
        <nav aria-label="About Patnam Pakodi">
          <p className="footer-label">Stay a little.</p>
          <SiteLink href="/about-us/">Our story</SiteLink>
          <SiteLink href="/franchise/">Own a franchise</SiteLink>
          <SiteLink href="/contact/">Get in touch</SiteLink>
          {(content?.pages ?? [])
            .filter((page) => page.slug.startsWith("policies/"))
            .map((page) => (
              <SiteLink key={page.slug} href={`/${page.slug}/`}>
                {page.heading}
              </SiteLink>
            ))}
        </nav>
        <div className="footer-message">
          Good company.
          <br />
          Great crunch.
        </div>
      </div>
      <div className="container footer-bottom">
        <span>
          © {new Date().getFullYear()} Patnam Pakodi · FRAB Foods India
        </span>
        <span>Made for the one-more-bite people.</span>
      </div>
    </footer>
  );
}
