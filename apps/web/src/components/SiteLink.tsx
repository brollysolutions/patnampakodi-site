import type { ComponentProps } from "react";

type Props = ComponentProps<"a"> & { href: string };

export function SiteLink({ href, ...props }: Props) {
  // Native navigation needs no link hydration or speculative fetch. A fresh
  // document also discards public analytics when entering a private flow.
  return <a href={href} {...props} />;
}
