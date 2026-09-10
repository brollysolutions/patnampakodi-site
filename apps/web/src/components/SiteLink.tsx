import Link from "next/link";
import type { ComponentProps } from "react";
import { PUBLIC_SLUGS, isPrivatePath } from "@/lib/policy.mjs";

type PublicSlug = (typeof PUBLIC_SLUGS)[number];
type PublicPath = "/" | `/${Exclude<PublicSlug, "home">}/`;
type Props = Omit<ComponentProps<typeof Link>, "href"> & { href: PublicPath };

export function SiteLink({ href, ...props }: Props) {
  // A fresh document discards any public analytics when entering a private flow.
  if (isPrivatePath(href)) return <a href={href} {...props} />;
  return <Link prefetch={false} href={{ pathname: href }} {...props} />;
}
