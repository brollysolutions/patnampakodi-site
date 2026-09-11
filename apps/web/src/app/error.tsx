"use client";

import { Icon } from "@/components/Icon";
import { SiteLink } from "@/components/SiteLink";

export default function PageError({ retry }: { retry: () => void }) {
  return (
    <section className="container section store-empty" role="alert">
      <title>Page unavailable | Patnam Pakodi</title>
      <Icon name="clock" />
      <h1>We couldn’t load this page</h1>
      <p>Please try again in a moment.</p>
      <div className="actions">
        <button className="button" onClick={retry}>
          Try again
        </button>
        <SiteLink className="button button-outline" href="/">
          Back to home
        </SiteLink>
      </div>
    </section>
  );
}
