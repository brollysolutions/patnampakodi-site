export function Notice({ message }: { message: string }) {
  return (
    <p className="notice" role="status" aria-live="polite">
      {message}
    </p>
  );
}
export function Field({
  name,
  label,
  type = "text",
  required = true,
  defaultValue,
  ...props
}: {
  name: string;
  label: string;
  type?: string;
  required?: boolean;
  defaultValue?: string | number;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "name">) {
  return (
    <label className="field">
      {label}
      <input
        name={name}
        type={type}
        required={required}
        defaultValue={defaultValue}
        {...props}
      />
    </label>
  );
}
