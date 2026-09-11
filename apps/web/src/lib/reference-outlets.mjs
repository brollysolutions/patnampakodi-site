/** @typedef {import("../../../../packages/contracts/schema").components["schemas"]["ContentBlock"]} Block */
/** @typedef {import("../../../../packages/contracts/schema").components["schemas"]["Outlet"]} Outlet */

/** Reconcile source sections with published outlet records, including removals.
 * @param {Block[]} blocks
 * @param {Outlet[]} outlets
 */
export function outletBlocks(blocks, outlets) {
  const records = new Map(outlets.map((outlet) => [outlet.slug, outlet]));
  /** @param {Block} block @param {Outlet} outlet @returns {Block} */
  function update(block, outlet) {
    if (block.kind === "heading" && block.text.startsWith("Patnam Pakodi"))
      return { ...block, text: `Patnam Pakodi – ${outlet.name}` };
    if (block.kind === "list" && block.children?.length === 3) {
      const [address, phone, hours] = block.children;
      return {
        ...block,
        children: [
          {
            ...address,
            text: outlet.address ?? `${outlet.city} ${outlet.pincode}`,
          },
          ...(outlet.phone
            ? [{ ...phone, text: outlet.phone, href: `tel:${outlet.phone}` }]
            : []),
          ...(outlet.hours ? [{ ...hours, text: outlet.hours }] : []),
        ],
      };
    }
    if (block.kind === "map")
      return {
        ...block,
        href: outlet.address
          ? `https://maps.google.com/maps?q=${encodeURIComponent(outlet.address)}&output=embed`
          : "",
      };
    if (
      block.kind === "enquiry" &&
      ["Directions", "Order Now"].includes(block.text)
    )
      return {
        ...block,
        kind: "link",
        href:
          block.text === "Directions"
            ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(outlet.address ?? `${outlet.name} ${outlet.city}`)}`
            : outlet.phone
              ? `tel:${outlet.phone}`
              : `/branches/${outlet.slug}/`,
      };
    return {
      ...block,
      children: (block.children ?? []).map((child) => update(child, outlet)),
    };
  }
  const result = blocks.flatMap((block) => {
    if (!block.record_slug) return [block];
    const outlet = records.get(block.record_slug);
    return outlet ? [update(block, outlet)] : [];
  });
  const represented = new Set(blocks.map((block) => block.record_slug));
  const base = blocks.find((block) => block.record_slug);
  if (base)
    for (const outlet of outlets) {
      if (represented.has(outlet.slug)) continue;
      result.push({
        ...base,
        record_slug: outlet.slug,
        layout: "column",
        children: [
          {
            ...base,
            kind: "heading",
            level: 2,
            text: outlet.name,
            children: [],
          },
          {
            ...base,
            kind: "text",
            text: outlet.address ?? `${outlet.city} ${outlet.pincode}`,
            children: [],
          },
          {
            ...base,
            kind: "link",
            text: "View branch",
            href: `/branches/${outlet.slug}/`,
            children: [],
          },
        ],
      });
    }
  return result;
}
