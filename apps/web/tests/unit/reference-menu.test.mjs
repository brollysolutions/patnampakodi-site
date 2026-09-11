import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { menuBlocks } from "../../src/lib/reference-menu.mjs";

const seed = JSON.parse(
  readFileSync(
    new URL("../../../api/content/storefront.json", import.meta.url),
    "utf8",
  ),
);
const blocks = seed.find((row) => row.kind === "page" && row.slug === "menu")
  .payload.blocks;
const items = seed
  .filter((row) => row.kind === "menu")
  .map((row) => row.payload);
const cards = (output) =>
  output.blocks
    .filter((block) => block.layout === "row")
    .flatMap((block) => block.children);

test("source menu artwork survives CMS rename, recategorization and price changes", () => {
  const changed = {
    ...items[0],
    name: "Updated dish",
    description: "Updated description",
    category: "Drinks",
    price_paise: 12300,
  };
  const output = menuBlocks(blocks, [changed], "Drinks", "updated");
  assert.equal(output.count, 1);
  const card = cards(output)[0];
  assert.equal(card.record_slug, changed.slug);
  assert.equal(card.children[1].text, changed.name);
  assert.equal(card.children[2].text, changed.description);
  assert.equal(card.children.at(-1).text, "₹123.00");
  assert.equal(
    card.children[0].children[0].image,
    blocks[1].children[0].children[0].children[0].image,
  );
});

test("unpublished records disappear and new records do not borrow another dish's photo", () => {
  assert.equal(menuBlocks(blocks, items.slice(1), "", "").count, 50);
  assert(
    !cards(menuBlocks(blocks, items.slice(1), "", "")).some(
      (card) => card.record_slug === items[0].slug,
    ),
  );
  const fresh = { ...items[0], slug: "new-dish", name: "New dish" };
  const card = cards(menuBlocks(blocks, [fresh], "", ""))[0];
  assert(
    card.children.every((block) => ["heading", "text"].includes(block.kind)),
  );
});

test("category and text search combine against authoritative CMS copy", () => {
  assert.equal(menuBlocks(blocks, items, "Drinks", "Kaju").count, 0);
  assert.equal(menuBlocks(blocks, items, "Drinks", "Junnu").count, 1);
});
