import "server-only";
import type { Route } from "next";
import { redirect } from "next/navigation";
import { getStorefront } from "./content";

export async function requireOrdering() {
  if (!(await getStorefront()).ordering_enabled) redirect("/menu/" as Route);
}
