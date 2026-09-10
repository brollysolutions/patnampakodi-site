"use client";

import {
  useEffect,
  useRef,
  useState,
  type FormEvent,
  type ReactNode,
} from "react";
import { api, jsonPost, type Schema } from "@/lib/commerce";

export function EnquiryProvider({ children }: { children: ReactNode }) {
  const [active, setActive] = useState<{
    label: string;
    trigger: HTMLButtonElement;
    key: string;
  } | null>(null);
  return (
    <div
      onClick={(event) => {
        if (!(event.target instanceof Element)) return;
        const trigger = event.target.closest<HTMLButtonElement>(
          "button[data-enquiry]",
        );
        if (trigger && event.currentTarget.contains(trigger))
          setActive({
            label: trigger.dataset.enquiry ?? "Franchise",
            trigger,
            key: crypto.randomUUID(),
          });
      }}
    >
      {children}
      {active && (
        <EnquiryDialog
          key={active.key}
          label={active.label}
          onDismiss={() => {
            active.trigger.focus();
            setActive(null);
          }}
        />
      )}
    </div>
  );
}

function EnquiryDialog({
  label,
  onDismiss,
}: {
  label: string;
  onDismiss: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    dialog.current?.showModal();
  }, []);
  const key = useRef<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [download, setDownload] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const brochure = /brochure/i.test(label);
  function close() {
    dialog.current?.close();
    onDismiss();
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || saved) return;
    const data = new FormData(event.currentTarget);
    let phone = String(data.get("phone")).replace(/[\s()-]/g, "");
    if (/^[6-9][0-9]{9}$/.test(phone)) phone = "+91" + phone;
    key.current ??= crypto.randomUUID();
    const query = new URLSearchParams(location.search);
    setBusy(true);
    setMessage("");
    try {
      const result = await api<Schema["QuickEnquiryReceipt"]>(
        "enquiries/quick",
        jsonPost({
          request_key: key.current,
          phone,
          purpose: brochure ? "brochure" : "franchise",
          source: query.get("utm_source")?.slice(0, 100) ?? "direct",
          campaign: query.get("utm_campaign")?.slice(0, 100) ?? "",
          medium: query.get("utm_medium")?.slice(0, 100) ?? "",
          website: String(data.get("website") ?? ""),
        }),
      );
      setSaved(true);
      setMessage(result.detail);
      setDownload(result.brochure_url);
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <dialog
      aria-label="Franchise enquiry"
      ref={dialog}
      className="enquiry-dialog"
      onCancel={(event) => {
        event.preventDefault();
        close();
      }}
      onClick={(event) => {
        if (event.target !== dialog.current) return;
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
      <button
        className="dialog-close"
        type="button"
        onClick={close}
        aria-label="Close enquiry"
      >
        ×
      </button>
      <h2>Start Your Patnam Pakodi Franchise Journey</h2>
      <form className="form-stack" onSubmit={submit}>
        <label className="field">
          Mobile Number
          <input
            name="phone"
            type="tel"
            inputMode="tel"
            autoComplete="tel"
            required
            pattern="(\+91)?[6-9][0-9]{9}"
            placeholder="10-digit mobile number"
            disabled={saved || busy}
            onChange={() => {
              key.current = null;
            }}
          />
        </label>
        <div hidden>
          <input name="website" tabIndex={-1} autoComplete="off" />
        </div>
        {!saved && (
          <button className="button" disabled={busy}>
            {busy ? "Saving…" : "Get Franchise Details"}
          </button>
        )}
        <p role="status">{message}</p>
        {download && (
          <a className="button" href={download} download>
            Download Brochure
          </a>
        )}
        {saved && brochure && !download && (
          <p>
            The approved brochure is not available online yet. Our team will
            help with your enquiry.
          </p>
        )}
        <p className="enquiry-privacy">
          Your number is used to respond to this enquiry.
        </p>
      </form>
    </dialog>
  );
}
