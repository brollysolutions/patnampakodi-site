"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { isPrivatePath } from "@/lib/policy.mjs";
import { BrowserReady } from "./BrowserReady";

declare global {
  interface Window {
    dataLayer?: unknown[];
    gtag?: (...args: unknown[]) => void;
  }
}

export function Analytics({ measurementId }: { measurementId: string }) {
  if (!/^G-[A-Z0-9]+$/.test(measurementId)) return null;
  return (
    <BrowserReady>
      <LoadedAnalytics measurementId={measurementId} />
    </BrowserReady>
  );
}
function LoadedAnalytics({ measurementId }: { measurementId: string }) {
  const path = usePathname();
  const [consent, setConsent] = useState(() => {
    try {
      return localStorage.getItem("pakodi-analytics") ?? "ask";
    } catch {
      return "deny";
    }
  });
  const enabled = /^G-[A-Z0-9]+$/.test(measurementId) && !isPrivatePath(path);
  useEffect(() => {
    if (!enabled || consent !== "allow") return;
    const location = window.location.origin + path;
    if (!window.gtag) {
      window.dataLayer = [];
      window.gtag = function (...args: unknown[]) {
        window.dataLayer!.push(args);
      };
      window.gtag("js", new Date());
      window.gtag("config", measurementId, {
        send_page_view: false,
        page_location: location,
        page_referrer: "",
        allow_google_signals: false,
        allow_ad_personalization_signals: false,
      });
      const script = document.createElement("script");
      script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
      script.async = true;
      script.referrerPolicy = "no-referrer";
      document.head.append(script);
    }
    window.gtag("event", "page_view", {
      page_location: location,
      page_referrer: "",
      page_title: document.title,
    });
  }, [enabled, consent, measurementId, path]);
  if (!enabled || consent === null) return null;
  function choose(value: string) {
    localStorage.setItem("pakodi-analytics", value);
    if (value === "deny" && consent === "allow") window.location.reload();
    else setConsent(value);
  }
  return (
    <aside className="container section" aria-label="Analytics preferences">
      {consent === "ask" ? (
        <div className="notice">
          <p>
            Allow optional analytics to help us improve our public website?
            Order and admin pages are excluded.
          </p>
          <div className="actions">
            <button
              className="button button-small"
              onClick={() => choose("allow")}
            >
              Allow analytics
            </button>
            <button
              className="button button-small"
              onClick={() => choose("deny")}
            >
              Decline analytics
            </button>
          </div>
        </div>
      ) : (
        <button
          className="button button-small"
          onClick={() => choose(consent === "allow" ? "deny" : "allow")}
        >
          {consent === "allow" ? "Turn off analytics" : "Allow analytics"}
        </button>
      )}
    </aside>
  );
}
