import { AdminPanel } from "@/components/AdminPanel";
import "./admin.css";
export const dynamic = "force-dynamic";
export const metadata = {
  title: "Administration | Patnam Pakodi",
  robots: { index: false, follow: false },
};
export default function AdminPage() {
  return (
    <section className="container section admin-page">
      <h1 className="sr-only">Administration</h1>
      <AdminPanel />
    </section>
  );
}
