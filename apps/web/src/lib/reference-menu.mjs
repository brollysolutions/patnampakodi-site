/** @typedef {import("../../../../packages/contracts/schema").components["schemas"]["ContentBlock"]} Block */
/** @typedef {import("../../../../packages/contracts/schema").components["schemas"]["MenuItem"]} Item */
export const menuCategories = ["Dry", "Wet", "Bowls", "Dips", "Drinks"];

/** Keep source card artwork/layout while using the published CMS records.
 * @param {Block[]} blocks
 * @param {Item[]} items
 * @param {string} category
 * @param {string} query
 */
export function menuBlocks(blocks, items, category, query) {
  const headings = blocks.filter((block) => block.layout !== "row");
  const row = blocks.find((block) => block.layout === "row");
  const base = row?.children[0];
  if (!row || !base) return { blocks: [], count: 0 };
  const heading = base.children.find((block) => block.kind === "heading");
  const copy = base.children.find((block) => block.kind === "text");
  if (!heading || !copy) return { blocks: [], count: 0 };
  const templates = new Map(
    blocks
      .filter((block) => block.layout === "row")
      .flatMap((block) => block.children)
      .map((block) => [block.record_slug, block]),
  );
  const q = query.trim().toLowerCase();
  const selected = items.filter(
    (item) =>
      (!category || item.category === category) &&
      (!q || `${item.name} ${item.description}`.toLowerCase().includes(q)),
  );
  /** @type {Block[]} */
  const result = [];
  for (const [index, name] of menuCategories.entries()) {
    const cards = selected
      .filter((item) => item.category === name)
      .map((item) => {
        const original = templates.get(item.slug);
        let named = false,
          described = false;
        const children = original
          ? original.children.map((block) => {
              if (block.kind === "heading" && !named) {
                named = true;
                return { ...block, text: item.name };
              }
              if (block.kind === "text" && !described) {
                described = true;
                return { ...block, text: item.description };
              }
              return block;
            })
          : [
              { ...heading, text: item.name },
              { ...copy, text: item.description },
            ];
        if (item.price_paise !== null)
          children.push({
            ...copy,
            text: new Intl.NumberFormat("en-IN", {
              style: "currency",
              currency: "INR",
            }).format(item.price_paise / 100),
          });
        return { ...(original ?? base), record_slug: item.slug, children };
      });
    if (!cards.length) continue;
    if (headings[index]) result.push(headings[index]);
    for (let offset = 0; offset < cards.length; offset += 4)
      result.push({ ...row, children: cards.slice(offset, offset + 4) });
  }
  return { blocks: result, count: selected.length };
}
