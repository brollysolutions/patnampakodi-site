import { SiteLink } from "@/components/SiteLink";
import { notFound } from "next/navigation";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
import { JsonLd } from "@/components/JsonLd";
type Props = { params: Promise<{ outlet: string }> };
export const dynamic = "force-dynamic";
async function find(props: Props) {
  const { outlet } = await props.params;
  const item = (await getStorefront()).outlets.find(
    (item) => item.slug === outlet,
  );
  if (!item) notFound();
  return item;
}
export async function generateMetadata(props: Props) {
  const outlet = await find(props);
  return pageMetadata({
    slug: "branches/" + outlet.slug,
    title: outlet.name + " outlet | Patnam Pakodi",
    description: `Find Patnam Pakodi in ${outlet.name}, ${outlet.city}. Check the outlet location, available contact details and opening hours before your visit.`,
    heading: outlet.name,
    intro: "",
    sections: [],
  });
}
export default async function OutletPage(props: Props) {
  const outlet = await find(props);
  const query =
    outlet.latitude != null && outlet.longitude != null
      ? `${outlet.latitude},${outlet.longitude}`
      : `Patnam Pakodi ${outlet.name} ${outlet.city}`;
  return (
    <section className="container section">
      <SiteLink href="/branches/">All outlets</SiteLink>
      <h1>Patnam Pakodi · {outlet.name}</h1>
      <div className="panel form-stack">
        <p>
          {outlet.address ??
            "Check the map listing for the current street address."}
        </p>
        <p>
          {outlet.city} · {outlet.pincode}
        </p>
        <p>
          {outlet.hours ?? "Check current opening hours before you travel."}
        </p>
        {outlet.phone && <a href={`tel:${outlet.phone}`}>{outlet.phone}</a>}
        <a
          className="button button-small"
          href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`}
          target="_blank"
          rel="noreferrer"
        >
          Open outlet map
        </a>
      </div>
      {outlet.address && (
        <JsonLd
          value={{
            "@context": "https://schema.org",
            "@type": "FoodEstablishment",
            name: `Patnam Pakodi ${outlet.name}`,
            address: {
              "@type": "PostalAddress",
              streetAddress: outlet.address,
              addressLocality: outlet.city,
              postalCode: outlet.pincode,
              addressCountry: "IN",
            },
            ...(outlet.phone ? { telephone: outlet.phone } : {}),
          }}
        />
      )}
    </section>
  );
}
