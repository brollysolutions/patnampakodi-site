import { AdminPanel } from "@/components/AdminPanel";
export const dynamic = "force-dynamic";
export const metadata = {
  title: "Administration | Patnam Pakodi",
  robots: { index: false, follow: false },
};
export default function AdminPage() {
  return (
    <section className="container section">
      <h1>Administration</h1>
      <AdminPanel />
    </section>
  );
}
