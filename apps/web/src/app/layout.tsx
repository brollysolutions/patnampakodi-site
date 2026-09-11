import type { Metadata } from "next";
import localFont from "next/font/local";
import { Header, Footer } from "@/components/Chrome";
import { SITE_URL } from "@/lib/policy.mjs";
import "./globals.css";
import "./commerce.css";
import "./reference.css";
import { AnalyticsGate } from "@/components/AnalyticsGate";

const display = localFont({
  src: "../../node_modules/@fontsource/abril-fatface/files/abril-fatface-latin-400-normal.woff2",
  variable: "--font-display",
  display: "swap",
  adjustFontFallback: "Times New Roman",
});
const body = localFont({
  src: "../../node_modules/@fontsource-variable/archivo/files/archivo-latin-wght-normal.woff2",
  variable: "--font-body",
  preload: true,
  display: "swap",
  weight: "400 700",
  adjustFontFallback: "Arial",
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  robots: { index: true, follow: true },
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
