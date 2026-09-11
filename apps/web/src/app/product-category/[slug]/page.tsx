import { notFound } from "next/navigation";
import { getCatalog } from "@/lib/catalog";
import { CatalogBrowser, label } from "@/components/CatalogBrowser";
import { pageMetadata } from "@/lib/seo";
export const dynamic = "force-dynamic";
type Props = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};
async function find(params: Props["params"]) {
  const { slug } = await params;
  if (!(await getCatalog()).some((item) => item.product.category === slug))
    notFound();
  return slug;
}
export async function generateMetadata({ params }: Props) {
  const slug = await find(params);
  return pageMetadata({
    slug: `product-category/${slug}`,
    title: label(slug) + " | Patnam Pakodi",
    description: "Browse " + label(slug) + " from Patnam Pakodi.",
    heading: label(slug),
    intro: "",
    sections: [],
    blocks: [],
  });
}
export default async function Archive({ params, searchParams }: Props) {
  return (
    <CatalogBrowser category={await find(params)} query={await searchParams} />
  );
}
