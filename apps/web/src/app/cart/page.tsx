import { Basket } from "@/components/Basket";
import { getCatalog } from "@/lib/catalog";
export const dynamic = "force-dynamic";
export const metadata = {
  title: "Your cart | Patnam Pakodi",
  robots: { index: false, follow: false },
};
export default async function CartPage({
  searchParams,
}: {
  searchParams: Promise<{ mode?: string }>;
}) {
  const query = await searchParams;
  return (
    <section className="container section">
      <h1>Your cart</h1>
      <Basket
        catalog={await getCatalog()}
        mode={
          query.mode === "fresh"
            ? "fresh"
            : query.mode === "packaged"
              ? "packaged"
              : undefined
        }
      />
      <noscript>
        Enable JavaScript to use your cart. You can still browse the menu and
        contact our team.
      </noscript>
    </section>
  );
}
