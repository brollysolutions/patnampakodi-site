import { headers } from "next/headers";
import { OrderManager } from "@/components/CommerceForms";
import { getStorefront } from "@/lib/content";
export const dynamic = "force-dynamic";
export const metadata = {
  title: "Your order | Patnam Pakodi",
  robots: { index: false, follow: false },
};
export default async function TrackPage() {
  return (
    <section className="container section">
      <h1>Your order</h1>
      <OrderManager
        nonce={(await headers()).get("x-nonce") ?? ""}
        orderingEnabled={(await getStorefront()).ordering_enabled}
      />
      <noscript>
        Enable JavaScript to securely access order details, or contact our team.
      </noscript>
    </section>
  );
}
