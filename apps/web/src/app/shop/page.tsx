import { requireOrdering } from "@/lib/ordering";
import { getStorefront } from "@/lib/content";
import { pageMetadata } from "@/lib/seo";
import { CatalogBrowser } from "@/components/CatalogBrowser";
export const dynamic = "force-dynamic";
export async function generateMetadata() {
  const content = await getStorefront();
  const page = content.pages.find((page) => page.slug === "shop");
  return page
    ? pageMetadata(page)
    : { title: "Packaged products | Patnam Pakodi" };
}
export default async function Shop({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  await requireOrdering();
  return <CatalogBrowser query={await searchParams} />;
}
