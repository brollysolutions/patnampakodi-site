import { notFound } from "next/navigation";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
type Props = { params: Promise<{ policy: string }> };
const allowed = ["shipping", "returns", "refunds", "privacy", "terms"];
export const dynamic = "force-dynamic";
async function find(props: Props) {
  const { policy } = await props.params;
  if (!allowed.includes(policy)) notFound();
  const page = (await getStorefront()).pages.find(
    (page) => page.slug === "policies/" + policy,
  );
  if (!page) notFound();
  return page;
}
export async function generateMetadata(props: Props) {
  return pageMetadata(await find(props));
}
export default async function PolicyPage(props: Props) {
  const page = await find(props);
  return (
    <section className="container section prose-sections">
      <h1>{page.heading}</h1>
      <p>{page.intro}</p>
      {page.sections.map((section) => (
        <section key={section.title}>
          <h2>{section.title}</h2>
          <p>{section.body}</p>
        </section>
      ))}
    </section>
  );
}
