import { CartForm } from "@/components/CommerceForms";
import { getCatalog } from "@/lib/catalog";
export const dynamic = "force-dynamic";
export const metadata = {
  title: "Your cart | Patnam Pakodi",
  robots: { index: false, follow: false },
};
export default async function CartPage() {
  return (
    <section className="container section">
      <h1>Your cart</h1>
      <CartForm catalog={await getCatalog()} />
      <noscript>
        Enable JavaScript to submit an order request. You can still browse the
        menu and contact our team.
      </noscript>
    </section>
  );
}
