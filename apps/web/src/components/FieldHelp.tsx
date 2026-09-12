"use client";

import {
  useId,
  useRef,
  useState,
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
} from "react";

type Help = { label: string; help: string };

function HelpControl({
  label,
  help,
  render,
  checkable = false,
}: Help & {
  render: (id: string, description: string) => ReactNode;
  checkable?: boolean;
}) {
  const id = useId();
  const [open, setOpen] = useState(false);
  const trigger = useRef<HTMLButtonElement>(null);
  const description = `${id}-help`;
  const control = render(id, description);
  return (
    <div className="field">
      <div className="field-caption">
        <label htmlFor={id} className={checkable ? "checkbox" : undefined}>
          {checkable && control}
          {label}
        </label>
        <button
          ref={trigger}
          type="button"
          className="field-info"
          aria-label={`Help for ${label}`}
          aria-expanded={open}
          aria-controls={description}
          onClick={() => setOpen((value) => !value)}
          onKeyDown={(event) => {
            if (event.key === "Escape") {
              setOpen(false);
              trigger.current?.focus();
            }
          }}
        >
          <span aria-hidden="true">i</span>
        </button>
      </div>
      {!checkable && control}
      <p id={description} className="field-help small" hidden={!open}>
        {help}
      </p>
    </div>
  );
}

export function HelpField({
  label,
  help,
  required = true,
  type = "text",
  ...props
}: Help & InputHTMLAttributes<HTMLInputElement>) {
  return (
    <HelpControl
      label={label}
      help={help}
      checkable={type === "checkbox"}
      render={(id, description) => (
        <input
          {...props}
          id={id}
          type={type}
          required={required}
          aria-describedby={description}
        />
      )}
    />
  );
}

export function HelpSelect({
  label,
  help,
  children,
  ...props
}: Help & SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <HelpControl
      label={label}
      help={help}
      render={(id, description) => (
        <select {...props} id={id} aria-describedby={description}>
          {children}
        </select>
      )}
    />
  );
}
