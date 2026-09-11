"use client";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useRef } from "react";
import { SiteLink } from "./SiteLink";
import { Icon } from "./Icon";
import { DeliveryDialog } from "./DeliveryDialog";
import { useShopping, updateShopping, type ShoppingMode } from "@/lib/shopping";
export function ShopNavigation() {
  const path = usePathname(),
    state = useShopping();
  const mode: ShoppingMode = path.startsWith("/menu")
    ? "fresh"
    : path.startsWith("/shop")
      ? "packaged"
      : state.mode;
  const count = state.carts[mode].reduce((sum, line) => sum + line.quantity, 0);
  const drawer = useRef<HTMLDialogElement>(null),
    trigger = useRef<HTMLButtonElement>(null);
  const choose = (value: ShoppingMode) => {
    try {
      updateShopping((current) => ({ ...current, mode: value }));
    } catch {
      /* Navigation works without storage. */
    }
  };
  const close = () => {
    drawer.current?.close();
    trigger.current?.focus();
  };
  const links = [
    ["Home", "/"],
    ["Order fresh", "/menu/"],
    ["Shop", "/shop/"],
    ["Our story", "/about-us/"],
    ["Branches", "/branches/"],
    ["Franchise", "/franchise/"],
    ["Contact", "/contact/"],
    ["Track order", "/track/"],
  ] as const;
  if (path === "/admin" || path.startsWith("/admin/"))
    return (
      <header className="admin-topbar">
        <div className="container">
          <SiteLink
            href="/"
            className="admin-brand"
            aria-label="Patnam Pakodi home"
          >
            <Image
              src="/images/live/656da99ddfd65b8a.webp"
              width={52}
              height={51}
              alt="Patnam Pakodi"
              priority
            />
            <span>
              <strong>Patnam Pakodi</strong>
              <small>Store administration</small>
            </span>
          </SiteLink>
          <SiteLink href="/" className="admin-store-link">
            View storefront <Icon name="arrow" />
          </SiteLink>
        </div>
      </header>
    );
  return (
    <>
      <aside className="store-announcement" aria-label="Store information">
        <span>Life Lo Spice Undali.</span>
        <SiteLink href="/branches/">
          Find your nearest Patnam Pakodi <Icon name="arrow" />
        </SiteLink>
      </aside>
      <header className="store-header">
        <div className="container store-header-main">
          <SiteLink
            className="store-logo"
            href="/"
            aria-label="Patnam Pakodi home"
          >
            <Image
              src="/images/live/656da99ddfd65b8a.webp"
              width={86}
              height={84}
              alt="Patnam Pakodi"
              priority
            />
          </SiteLink>
          <DeliveryDialog mode={mode} />
          <form
            className="store-search"
            action={mode === "fresh" ? "/menu/" : "/shop/"}
            method="get"
            role="search"
          >
            <label className="sr-only" htmlFor="site-search">
              Search {mode === "fresh" ? "fresh food" : "packaged products"}
            </label>
            <input
              id="site-search"
              type="search"
              name="q"
              maxLength={100}
              placeholder={
                mode === "fresh"
                  ? "Find your next favourite bite…"
                  : "Search ready mixes & more…"
              }
            />
            <button aria-label="Search">
              <Icon name="search" />
            </button>
          </form>
          <div className="store-tools">
            <SiteLink
              href="/favourites/"
              className="store-tool"
              aria-label="Favourites"
            >
              <Icon name="heart" />
              <span>Favourites</span>
            </SiteLink>
            <SiteLink
              href={`/cart/?mode=${mode}`}
              className="store-tool"
              aria-label={`Cart, ${count} items`}
            >
              <span className="cart-icon">
                <Icon name="bag" />
                <b>{count}</b>
              </span>
              <span>Cart</span>
            </SiteLink>
            <button
              ref={trigger}
              className="icon-button mobile-menu-button"
              aria-label="Open menu"
              onClick={() => drawer.current?.showModal()}
            >
              <Icon name="menu" />
            </button>
          </div>
        </div>
        <div className="store-nav-row">
          <div className="container">
            <nav className="shopping-modes" aria-label="Shopping modes">
              <SiteLink
                href="/menu/"
                aria-current={path.startsWith("/menu") ? "page" : undefined}
                onClick={() => choose("fresh")}
              >
                <Icon name="fresh" />
                Order fresh
              </SiteLink>
              <SiteLink
                href="/shop/"
                aria-current={path.startsWith("/shop") ? "page" : undefined}
                onClick={() => choose("packaged")}
              >
                <Icon name="box" />
                Shop packaged
              </SiteLink>
            </nav>
            <nav className="store-secondary-nav" aria-label="Main navigation">
              {links
                .filter(([, href]) => !["/", "/menu/", "/shop/"].includes(href))
                .map(([label, href]) => (
                  <SiteLink
                    key={href}
                    href={href}
                    aria-current={path === href ? "page" : undefined}
                  >
                    {label}
                  </SiteLink>
                ))}
            </nav>
          </div>
        </div>
      </header>
      <dialog
        ref={drawer}
        className="store-drawer"
        onClick={(event) => {
          if (event.target === drawer.current) {
            const bounds = event.currentTarget.getBoundingClientRect();
            if (
              event.clientX < bounds.left ||
              event.clientX > bounds.right ||
              event.clientY < bounds.top ||
              event.clientY > bounds.bottom
            )
              close();
          }
        }}
        onCancel={close}
      >
        <div className="drawer-heading">
          <strong>Explore Patnam Pakodi</strong>
          <button
            className="icon-button"
            aria-label="Close menu"
            onClick={close}
          >
            <Icon name="close" />
          </button>
        </div>
        <nav aria-label="Mobile navigation">
          {links.map(([label, href]) => (
            <SiteLink
              key={href}
              href={href}
              onClick={() => {
                if (href === "/menu/") choose("fresh");
                if (href === "/shop/") choose("packaged");
                close();
              }}
            >
              {label}
              <Icon name="chevron" />
            </SiteLink>
          ))}
        </nav>
      </dialog>
      <nav className="mobile-bottom-nav" aria-label="Quick shopping navigation">
        <SiteLink href="/" aria-current={path === "/" ? "page" : undefined}>
          <Icon name="home" />
          Home
        </SiteLink>
        <SiteLink
          href="/menu/"
          onClick={() => choose("fresh")}
          aria-current={path === "/menu/" ? "page" : undefined}
        >
          <Icon name="fresh" />
          Fresh
        </SiteLink>
        <SiteLink
          href="/shop/"
          onClick={() => choose("packaged")}
          aria-current={path === "/shop/" ? "page" : undefined}
        >
          <Icon name="box" />
          Shop
        </SiteLink>
        <SiteLink href="/favourites/">
          <Icon name="heart" />
          Saved
        </SiteLink>
        <SiteLink href={`/cart/?mode=${mode}`}>
          <Icon name="bag" />
          Cart ({count})
        </SiteLink>
      </nav>
    </>
  );
}
