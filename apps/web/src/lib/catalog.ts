import "server-only";
import type { Schema } from "./commerce";

export async function getCatalog(): Promise<Schema["VariantView"][]> {
  const response = await fetch(
    `${process.env.CONTENT_API_URL ?? "http://127.0.0.1:8000"}/v1/catalog`,
    { cache: "no-store", signal: AbortSignal.timeout(5000) },
  );
  if (!response.ok) throw new Error("The shop is temporarily unavailable.");
  return response.json();
}
