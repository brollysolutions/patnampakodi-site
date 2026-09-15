import { requireOrdering } from "@/lib/ordering";
import { notFound, permanentRedirect } from "next/navigation";
import { getCatalog } from "@/lib/catalog";
import type { Route } from "next";
export const dynamic = "force-dynamic";
export default async function LegacyProduct({
  params,
}: {
  params: Promise<{ product: string }>;
}) {
  await requireOrdering();
  const { product } = await params;
  if (!(await getCatalog()).some((item) => item.product.slug === product))
    notFound();
  permanentRedirect(`/product/${product}/` as Route);
}
