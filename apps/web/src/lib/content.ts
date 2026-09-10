import "server-only";
import { cache } from "react";
import type { components } from "../../../../packages/contracts/schema";

export type Storefront = components["schemas"]["Storefront"];
export type PageContent = components["schemas"]["Page"];
export type MenuItem = components["schemas"]["MenuItem"];
export type Outlet = components["schemas"]["Outlet"];

export const getStorefront = cache(async (): Promise<Storefront> => {
  const base = process.env.CONTENT_API_URL ?? "http://127.0.0.1:8000";
  const response = await fetch(`${base}/v1/storefront`, {
    cache: "no-store",
    signal: AbortSignal.timeout(5000),
  });
  if (!response.ok)
    throw new Error(
      "The menu is temporarily unavailable. Please try again shortly.",
    );
  return response.json() as Promise<Storefront>;
});
