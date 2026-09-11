"use client";
import { useRef, type ReactNode } from "react";
import { Icon } from "./Icon";
export function CatalogFilters({ children }: { children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null),
    trigger = useRef<HTMLButtonElement>(null);
  const close = () => {
    dialog.current?.close();
    trigger.current?.focus();
  };
  return (
    <>
      <div className="catalog-filter-panel filter-desktop">
        <h2>
          <Icon name="filter" />
          Filter your favourites
        </h2>
        {children}
      </div>
      <noscript>
        <div className="catalog-filter-panel filter-fallback">
          <h2>Filter your favourites</h2>
          {children}
        </div>
      </noscript>
      <button
        className="button button-outline filter-launch"
        ref={trigger}
        onClick={() => dialog.current?.showModal()}
      >
        <Icon name="filter" />
        Filter &amp; sort
      </button>
      <dialog
        ref={dialog}
        className="filter-sheet"
        aria-labelledby="filter-title"
        onCancel={close}
        onClick={(event) => {
          if (event.target === dialog.current) {
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
      >
        <div className="drawer-heading">
          <h2 id="filter-title">Filter &amp; sort</h2>
          <button
            className="icon-button"
            aria-label="Close filters"
            onClick={close}
          >
            <Icon name="close" />
          </button>
        </div>
        {children}
      </dialog>
    </>
  );
}
