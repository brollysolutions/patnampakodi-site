import "server-only";
import { cache } from "react";
import { fetchStorefront } from "./content-request.mjs";
import type { components } from "../../../../packages/contracts/schema";

export type Storefront = components["schemas"]["Storefront"];
export type PageContent = components["schemas"]["Page"];
export type MenuItem = components["schemas"]["MenuItem"];
export type Outlet = components["schemas"]["Outlet"];

export const getStorefront = cache(async (): Promise<Storefront> => {
  const base = process.env.CONTENT_API_URL ?? "http://127.0.0.1:8500";
  return fetchStorefront(base) as Promise<Storefront>;
});
