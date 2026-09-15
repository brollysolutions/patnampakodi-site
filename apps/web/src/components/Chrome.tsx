import { getStorefront } from "@/lib/content";
import { SiteLink } from "./SiteLink";
import { ShopNavigation } from "./ShopNavigation";
import { Icon } from "./Icon";
import { BrandMark } from "./BrandMark";
export function Wordmark() {
  return <BrandMark />;
}
export function Header() {
  return <ShopNavigation />;
}
export async function Footer() {
  const content = await getStorefront().catch(() => null);
  return (
    <footer className="store-footer">
      <div className="container footer-top">
        <div className="footer-brand">
          <Wordmark />
          <h2>
            A little spice.
            <br />A lot of good company.
          </h2>
          <p>
            Four dry chicken pakodi flavours. Currently serving only in
            Kukatpally, Hyderabad.
          </p>
        </div>
        <nav aria-label="Discover Patnam Pakodi">
          <h3>Get to know us</h3>
          <SiteLink href="/menu/">Our menu</SiteLink>
          <SiteLink href="/about-us/">Our story</SiteLink>
          <SiteLink href="/branches/">Visit Kukatpally</SiteLink>
          <SiteLink href="/franchise/">Become a franchise partner</SiteLink>
          <SiteLink href="/contact/">Contact us</SiteLink>
        </nav>
        <div className="footer-contact">
          <h3>Let’s talk</h3>
          <p>Central contact for brand and franchise enquiries.</p>
          {content?.contact_phone && (
            <a href={`tel:${content.contact_phone}`}>
              <Icon name="phone" />
              {content.contact_phone}
            </a>
          )}
          {content?.contact_email && (
            <a href={`mailto:${content.contact_email}`}>
              <Icon name="mail" />
              {content.contact_email}
            </a>
          )}
          <SiteLink className="text-link" href="/contact/">
            We’re here to help <Icon name="arrow" />
          </SiteLink>
        </div>
      </div>
      <div className="container footer-legal">
        <span>
          © {new Date().getFullYear()} Patnam Pakodi · FRAB Foods India
        </span>
        <nav aria-label="Policies">
          {content?.pages
            .filter((page) => page.slug.startsWith("policies/"))
            .map((page) => (
              <a key={page.slug} href={`/${page.slug}/`}>
                {page.heading}
              </a>
            ))}
        </nav>
      </div>
    </footer>
  );
}
