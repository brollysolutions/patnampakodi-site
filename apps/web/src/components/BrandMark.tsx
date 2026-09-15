import Image from "next/image";
import { SiteLink } from "./SiteLink";

export function BrandMark({ priority = false }: { priority?: boolean }) {
  return (
    <SiteLink
      href="/"
      className="store-logo editorial-brand"
      aria-label="Patnam Pakodi home"
    >
      <Image
        src="/images/live/patnam-logo-refined.webp"
        alt=""
        width={600}
        height={600}
        sizes="96px"
        priority={priority}
      />
      <span>
        <strong>Patnam Pakodi</strong>
        <small>Life Lo Spice Undali.</small>
      </span>
    </SiteLink>
  );
}
