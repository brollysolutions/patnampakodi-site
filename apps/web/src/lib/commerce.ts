import type { components } from "../../../../packages/contracts/schema";

export type Schema = components["schemas"];
export const money = (paise: number) =>
  new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(
    paise / 100,
  );
export const statusLabel = (status: string) =>
  ({
    requested: "Awaiting delivery confirmation",
    approved: "Ready for payment",
    payment_pending: "Payment confirmation pending",
    paid: "Payment confirmed",
    preparing: "Preparing your food",
    dispatched: "Dispatched",
    delivered: "Delivered",
    delivery_issue: "Delivery needs attention",
    declined: "Unable to fulfill",
    cancelled: "Cancelled",
    refund_pending: "Refund in progress",
    refunded: "Refund completed",
  })[status] ?? status.replaceAll("_", " ");

export async function api<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const csrf =
    typeof document === "undefined"
      ? ""
      : document.cookie
          .split("; ")
          .find((part) => part.startsWith("pakodi_csrf="))
          ?.split("=")[1];
  const response = await fetch("/api/v1/" + path, {
    ...options,
    cache: "no-store",
    headers: {
      ...(options.body && typeof options.body === "string"
        ? { "Content-Type": "application/json" }
        : {}),
      ...(csrf ? { "X-CSRF-Token": csrf } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const result = await response.json().catch(() => null);
    throw new Error(
      typeof result?.detail === "string"
        ? result.detail
        : "Please check the form fields and try again.",
    );
  }
  return response.json();
}

export const jsonPost = (body: unknown): RequestInit => ({
  method: "POST",
  body: JSON.stringify(body),
});
