import Image from "next/image";
import type { MenuItem } from "@/lib/content";
import { SIGNATURE_SLUGS } from "@/lib/policy.mjs";

export function MenuGrid({
  items,
  headingLevel = 3,
  expanded = false,
}: {
  items: MenuItem[];
  headingLevel?: 2 | 3;
  expanded?: boolean;
}) {
  const Heading = headingLevel === 2 ? "h2" : "h3";
  const flavours = SIGNATURE_SLUGS.flatMap((slug) =>
    items.filter((item) => item.slug === slug),
  );
  return (
    <div
      className={`signature-grid${expanded ? " signature-grid-expanded" : ""}`}
    >
      {flavours.map((item) => (
        <article className="signature-item" key={item.slug}>
          {item.image && (
            <Image
              src={item.image}
              alt={`Illustration of ${item.name}`}
              width={1024}
              height={1024}
              sizes={
                expanded
                  ? "(max-width: 767px) 92vw, 45vw"
                  : "(max-width: 599px) 92vw, (max-width: 1000px) 44vw, 280px"
              }
            />
          )}
          <div>
            <Heading>{item.name}</Heading>
            <p>{item.description}</p>
            {expanded && (
              <p className="flavour-visit">
                Discover this flavour at Kukatpally.
              </p>
            )}
          </div>
        </article>
      ))}
      {!flavours.length && (
        <p>
          Our menu is being updated. Please contact our team for flavour
          details.
        </p>
      )}
    </div>
  );
}
