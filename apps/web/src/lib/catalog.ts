import "server-only";
import type { Schema } from "./commerce";
import type { operations } from "../../../../packages/contracts/schema";
export type CatalogQuery = NonNullable<
  operations["catalog_v1_catalog_get"]["parameters"]["query"]
>;
export async function getCatalog(
  query: CatalogQuery = {},
): Promise<Schema["VariantView"][]> {
  const url = new URL(
    `${process.env.CONTENT_API_URL ?? "http://127.0.0.1:8000"}/v1/catalog`,
  );
  for (const [name, value] of Object.entries(query))
    if (value !== undefined && value !== "")
      url.searchParams.set(name, String(value));
  const response = await fetch(url, {
    cache: "no-store",
    signal: AbortSignal.timeout(5000),
  });
  if (!response.ok) throw new Error("The shop is temporarily unavailable.");
  return response.json();
}
