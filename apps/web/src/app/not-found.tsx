import { SiteLink } from "@/components/SiteLink";

export default function NotFound() {
  return (
    <section className="container empty-state not-found">
      <p>404</p>
      <h1>This bite is missing.</h1>
      <p>That page isn’t available. There’s still plenty to explore.</p>
      <SiteLink className="button button-primary" href="/menu/">
        Explore the menu
      </SiteLink>
    </section>
  );
}
