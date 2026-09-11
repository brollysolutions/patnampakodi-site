"use client";
import { useSyncExternalStore } from "react";
import {
  SHOPPING_KEY,
  EMPTY_SHOPPING,
  parseShopping,
  cleanLines,
} from "./shopping-state.mjs";
import type { Schema } from "./commerce";
export type ShoppingMode = "fresh" | "packaged";
export type ShoppingState = {
  mode: ShoppingMode;
  carts: Record<ShoppingMode, Schema["CartLine"][]>;
  favourites: string[];
};
export function shoppingSnapshot() {
  try {
    const saved = localStorage.getItem(SHOPPING_KEY);
    if (saved) return saved;
    const old = localStorage.getItem("pakodi-cart-v1");
    if (old)
      return JSON.stringify({
        ...JSON.parse(EMPTY_SHOPPING),
        carts: { fresh: [], packaged: cleanLines(JSON.parse(old)) },
      });
  } catch {
    /* Browsing remains available when storage is unavailable. */
  }
  return EMPTY_SHOPPING;
}
function subscribe(callback: () => void) {
  window.addEventListener("storage", callback);
  window.addEventListener("pakodi-shopping", callback);
  window.addEventListener("pageshow", callback);
  return () => {
    window.removeEventListener("storage", callback);
    window.removeEventListener("pakodi-shopping", callback);
    window.removeEventListener("pageshow", callback);
  };
}
export function useShopping(): ShoppingState {
  return parseShopping(
    useSyncExternalStore(subscribe, shoppingSnapshot, () => EMPTY_SHOPPING),
  ) as ShoppingState;
}
export function updateShopping(
  change: (state: ShoppingState) => ShoppingState,
) {
  const next = change(parseShopping(shoppingSnapshot()) as ShoppingState);
  localStorage.setItem(SHOPPING_KEY, JSON.stringify(next));
  window.dispatchEvent(new Event("pakodi-shopping"));
}
