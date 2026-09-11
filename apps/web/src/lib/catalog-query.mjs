/** Normalize URL form input before making the typed public catalog request.
 * @param {Record<string, string | string[] | undefined>} query
 * @returns {import('./catalog').CatalogQuery}
 */
export function normalizeCatalogQuery(query) {
  const value = (name) =>
    typeof query[name] === "string" ? query[name].trim() : "";
  const slug = (name) =>
    value(name).length <= 80 && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value(name))
      ? value(name)
      : "";
  const max = Number(value("max"));
  const sort = value("sort");
  const dietary = value("dietary");
  return {
    q: value("q").slice(0, 100),
    category: slug("category"),
    tag: slug("tag"),
    dietary: dietary === "veg" || dietary === "non-veg" ? dietary : "",
    max_price:
      value("max") && Number.isFinite(max) && max >= 0 && max <= 1000000
        ? Math.round(max * 100)
        : undefined,
    sort:
      sort === "price-asc" || sort === "price-desc" || sort === "name"
        ? sort
        : "default",
  };
}
