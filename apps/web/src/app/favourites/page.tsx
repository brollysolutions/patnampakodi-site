import { Favourites } from "@/components/Basket";
import { getCatalog } from "@/lib/catalog";
export const dynamic = "force-dynamic";
export const metadata = {
  title: "Your favourites | Patnam Pakodi",
  robots: { index: false, follow: false },
};
export default async function FavouritesPage() {
  return (
    <section className="container section">
      <h1>Your favourites</h1>
      <Favourites catalog={await getCatalog()} />
      <noscript>Enable JavaScript to save favourites on this device.</noscript>
    </section>
  );
}
