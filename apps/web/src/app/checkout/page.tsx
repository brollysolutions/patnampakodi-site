import { requireOrdering } from "@/lib/ordering";
import { Basket } from "@/components/Basket";
import { getCatalog } from "@/lib/catalog";
export const dynamic = "force-dynamic";
export const metadata = {
  title: "Checkout | Patnam Pakodi",
  robots: { index: false, follow: false },
};
export default async function CheckoutPage({
  searchParams,
}: {
  searchParams: Promise<{ mode?: string }>;
}) {
  await requireOrdering();
  const query = await searchParams;
  return (
    <section className="container section">
      <h1>Checkout</h1>
      <Basket
        catalog={await getCatalog()}
        mode={
          query.mode === "fresh"
            ? "fresh"
            : query.mode === "packaged"
              ? "packaged"
              : undefined
        }
        checkout
      />
      <noscript>
        Enable JavaScript for secure checkout, or contact our team for help.
      </noscript>
    </section>
  );
}
