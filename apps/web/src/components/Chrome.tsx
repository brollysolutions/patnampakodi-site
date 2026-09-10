import { SiteLink } from "./SiteLink";
import { getStorefront } from "@/lib/content";

const links = [
  ["Menu", "/menu/"],
  ["Shop", "/shop/"],
  ["Our story", "/about-us/"],
  ["Find a store", "/branches/"],
  ["Cart", "/cart/"],
] as const;

const mobileLinks = [
  ...links,
  ["Own a franchise", "/franchise/"],
  ["Contact", "/contact/"],
] as const;

export function Wordmark() {
  return (
    <SiteLink className="wordmark" href="/" aria-label="Patnam Pakodi home">
      Patnam
      <span>
        Pakodi<span className="wordmark-dot">.</span>
      </span>
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
        <SiteLink
          className="button button-small header-franchise"
          href="/franchise/"
        >
          Own a franchise <span aria-hidden="true">↗</span>
        </SiteLink>
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
