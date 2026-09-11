import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { outletBlocks } from "../../src/lib/reference-outlets.mjs";
const seed = JSON.parse(
  readFileSync(
    new URL("../../../api/content/storefront.json", import.meta.url),
    "utf8",
  ),
);
const blocks = seed.find(
  (row) => row.kind === "page" && row.slug === "branches",
).payload.blocks;
const outlets = seed
  .filter((row) => row.kind === "outlet")
  .map((row) => row.payload);
function flatten(blocks) {
  return blocks.flatMap((block) => [block, ...flatten(block.children ?? [])]);
}
test("outlet unpublishing removes headings, cards, phone and map together", () => {
  const output = outletBlocks(blocks, outlets.slice(1));
  assert(!output.some((block) => block.record_slug === outlets[0].slug));
  assert.equal(output.filter((block) => block.record_slug).length, 10);
});
test("outlet staff edits reach visible details, directions and map", () => {
  const outlet = {
    ...outlets[0],
    name: "Updated branch",
    address: "Updated address",
    phone: "+919123456789",
    hours: "Updated hours",
  };
  const output = flatten(
    outletBlocks(blocks, [outlet]).filter((block) => block.record_slug),
  );
  assert(
    output.some((block) => block.text === "Patnam Pakodi – Updated branch"),
  );
  assert(output.some((block) => block.text === "Updated address"));
  assert(output.some((block) => block.text === "Updated hours"));
  assert(output.some((block) => block.href === "tel:+919123456789"));
  assert(
    output.some(
      (block) =>
        block.kind === "map" && block.href.includes("Updated%20address"),
    ),
  );
});
test("new published outlets appear without borrowing photographs", () => {
  const output = outletBlocks(blocks, [{ ...outlets[0], slug: "new-branch" }]);
  const added = output.find((block) => block.record_slug === "new-branch");
  assert(added);
  assert(!flatten([added]).some((block) => block.kind === "image"));
});
