"use client";
import { useRef } from "react";
import { DeliveryCheck } from "./DeliveryCheck";
import { Icon } from "./Icon";
import type { ShoppingMode } from "@/lib/shopping";
export function DeliveryDialog({ mode }: { mode: ShoppingMode }) {
  const dialog = useRef<HTMLDialogElement>(null),
    trigger = useRef<HTMLButtonElement>(null);
  const close = () => {
    dialog.current?.close();
    trigger.current?.focus();
  };
  return (
    <>
      <button
        ref={trigger}
        className="delivery-trigger"
        onClick={() => dialog.current?.showModal()}
      >
        <Icon name="pin" />
        <span>
          Delivering to you?<strong>Check your PIN</strong>
        </span>
      </button>
      <dialog
        ref={dialog}
        className="delivery-dialog"
        aria-label="Check delivery availability"
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
          <h2>Check delivery</h2>
          <button
            className="icon-button"
            aria-label="Close delivery check"
            onClick={close}
          >
            <Icon name="close" />
          </button>
        </div>
        <DeliveryCheck key={mode} mode={mode} />
      </dialog>
    </>
  );
}
