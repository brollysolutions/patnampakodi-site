export const SITE_URL = "https://patnampakodi.com";
export const PUBLIC_SLUGS = [
  "home",
  "about-us",
  "menu",
  "shop",
  "branches",
  "franchise",
  "contact",
];
export const PRIVATE_PREFIXES = [
  "admin",
  "account",
  "cart",
  "checkout",
  "track",
  "api",
  "preview",
];

export function pathFor(slug) {
  return slug === "home" ? "/" : `/${slug}/`;
}

export function isPrivatePath(path) {
  return PRIVATE_PREFIXES.includes(
    path.split("/").filter(Boolean)[0]?.toLowerCase(),
  );
}

export function indexable(environment) {
  // Production NODE_ENV is also used for preview builds and must not grant indexing.
  return (
    environment.SITE_INDEXABLE === "true" &&
    environment.DEPLOYMENT_ENV !== "preview"
  );
}

export function serializeJsonLd(value) {
  return JSON.stringify(value).replace(/</g, "\\u003c");
}

export function filterMenu(items, category, query) {
  const normalized = query.trim().toLowerCase();
  return items.filter(
    (item) =>
      (!category || item.category === category) &&
      (!normalized ||
        `${item.name} ${item.description}`.toLowerCase().includes(normalized)),
  );
}

export function filterOutlets(items, query) {
  const normalized = query.trim().toLowerCase();
  return items.filter((item) =>
    `${item.name} ${item.city} ${item.pincode}`
      .toLowerCase()
      .includes(normalized),
  );
}
