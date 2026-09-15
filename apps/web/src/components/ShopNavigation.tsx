"use client";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useRef } from "react";
import { SiteLink } from "./SiteLink";
import { Icon } from "./Icon";
import { NAVIGATION } from "@/lib/policy.mjs";

export function ShopNavigation() {
  const path = usePathname();
  const drawer = useRef<HTMLDialogElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const close = () => {
    drawer.current?.close();
    trigger.current?.focus();
  };
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
            View website <Icon name="arrow" />
          </SiteLink>
        </div>
      </header>
    );
  return (
    <>
      <aside className="store-announcement" aria-label="Brand information">
        <span>Life Lo Spice Undali.</span>
        <SiteLink href="/branches/">
          Find your nearest Patnam Pakodi <Icon name="arrow" />
        </SiteLink>
      </aside>
      <header className="store-header menu-header">
        <div className="container menu-header-inner">
          <SiteLink
            className="store-logo"
            href="/"
            aria-label="Patnam Pakodi home"
          >
            <Image
              src="/images/live/656da99ddfd65b8a.webp"
              width={70}
              height={68}
              alt="Patnam Pakodi"
              priority
            />
          </SiteLink>
          <nav className="menu-desktop-nav" aria-label="Main navigation">
            {NAVIGATION.map(([label, href]) => (
              <SiteLink
                key={href}
                href={href}
                aria-current={
                  path.replace(/\/$/, "") === href.replace(/\/$/, "")
                    ? "page"
                    : undefined
                }
              >
                {label}
              </SiteLink>
            ))}
          </nav>
          <button
            ref={trigger}
            className="icon-button menu-toggle"
            aria-label="Open menu"
            aria-haspopup="dialog"
            onClick={() => drawer.current?.showModal()}
          >
            <Icon name="menu" />
          </button>
          <noscript>
            <nav
              className="menu-nojs-nav"
              aria-label="Navigation without JavaScript"
            >
              {NAVIGATION.map(([label, href]) => (
                <SiteLink key={href} href={href}>
                  {label}
                </SiteLink>
              ))}
            </nav>
          </noscript>
        </div>
      </header>
      <dialog
        ref={drawer}
        className="store-drawer"
        aria-label="Main menu"
        onCancel={(event) => {
          event.preventDefault();
          close();
        }}
        onClick={(event) => {
          if (event.target !== drawer.current) return;
          const bounds = event.currentTarget.getBoundingClientRect();
          if (
            event.clientX < bounds.left ||
            event.clientX > bounds.right ||
            event.clientY < bounds.top ||
            event.clientY > bounds.bottom
          )
            close();
        }}
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
          {NAVIGATION.map(([label, href]) => (
            <SiteLink key={href} href={href} onClick={close}>
              {label}
              <Icon name="chevron" />
            </SiteLink>
          ))}
        </nav>
      </dialog>
    </>
  );
}
