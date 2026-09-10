"use client";

import { useSyncExternalStore, type ReactNode } from "react";

const subscribe = () => () => {};
export function BrowserReady({ children }: { children: ReactNode }) {
  const ready = useSyncExternalStore(
    subscribe,
    () => true,
    () => false,
  );
  return ready ? children : <p role="status">Loading…</p>;
}
