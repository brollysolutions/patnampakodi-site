import type { Metadata } from "next";
import localFont from "next/font/local";
import { Header, Footer } from "@/components/Chrome";
import { indexable, SITE_URL } from "@/lib/policy.mjs";
import "./globals.css";
import "./commerce.css";
import "./reference.css";
import "./store.css";
import { AnalyticsGate } from "@/components/AnalyticsGate";

const display = localFont({
  src: "../../node_modules/@fontsource-variable/inter/files/inter-latin-wght-normal.woff2",
  variable: "--font-display",
  display: "swap",
  weight: "400 800",
  preload: false,
  adjustFontFallback: "Arial",
});
const body = localFont({
  src: [
    {
      path: "../../node_modules/@fontsource/poppins/files/poppins-latin-400-normal.woff2",
      weight: "400",
    },
    {
      path: "../../node_modules/@fontsource/poppins/files/poppins-latin-500-normal.woff2",
      weight: "500",
    },
    {
      path: "../../node_modules/@fontsource/poppins/files/poppins-latin-600-normal.woff2",
      weight: "600",
    },
    {
      path: "../../node_modules/@fontsource/poppins/files/poppins-latin-700-normal.woff2",
      weight: "700",
    },
    {
      path: "../../node_modules/@fontsource/poppins/files/poppins-latin-800-normal.woff2",
      weight: "800",
    },
  ],
  variable: "--font-body",
  preload: true,
  display: "swap",
  adjustFontFallback: "Arial",
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  robots: { index: indexable(process.env), follow: indexable(process.env) },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en-IN" className={`${display.variable} ${body.variable}`}>
      <body>
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        <Header />
        <main id="main">{children}</main>
        <Footer />
        <AnalyticsGate />
      </body>
    </html>
  );
}
