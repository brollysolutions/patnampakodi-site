"use client";
import { useState, type FormEvent } from "react";
import { api, jsonPost, type Schema } from "@/lib/commerce";
import { Field, Notice } from "./FormFields";

export function FranchiseForm() {
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const attribution = new URLSearchParams(window.location.search);
    setBusy(true);
    try {
      const result = await api<Schema["ActionResult"]>(
        "enquiries",
        jsonPost({
          ...Object.fromEntries(data),
          source: attribution.get("utm_source") ?? "direct",
          campaign: attribution.get("utm_campaign") ?? "",
          medium: attribution.get("utm_medium") ?? "",
        }),
      );
      setMessage(result.detail);
      form.reset();
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="panel form-stack" onSubmit={submit}>
      <h2>Let’s talk franchise</h2>
      <Field name="name" label="Full name" minLength={2} maxLength={100} />
      <Field
        name="phone"
        label="Phone including +91"
        type="tel"
        pattern="\+91[6-9][0-9]{9}"
      />
      <Field name="email" label="Email" type="email" maxLength={254} />
      <Field name="city" label="City" minLength={2} maxLength={100} />
      <Field
        name="preferred_model"
        label="Preferred franchise model"
        minLength={2}
        maxLength={100}
      />
      <Field name="budget" label="Budget range" maxLength={100} />
      <div hidden aria-hidden="true">
        <input name="website" tabIndex={-1} autoComplete="off" />
      </div>
      <button className="button" disabled={busy}>
        {busy ? "Saving…" : "Send enquiry"}
      </button>
      <Notice message={message} />
    </form>
  );
}
