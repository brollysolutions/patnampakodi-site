import test from "node:test";
import assert from "node:assert/strict";
import { outletBlocks } from "../../src/lib/reference-outlets.mjs";
// The legacy block renderer remains supported. Its fixtures must not depend on
// the current editorial page, which now renders a single published outlet.
const outlets = ["first", "second"].map((slug) => ({
  slug,
  name: `${slug} fixture`,
  city: "Fixture city",
  pincode: "500001",
  address: `${slug} fixture address`,
  phone: "+919123456789",
  hours: "Fixture hours",
}));
const blocks = outlets.flatMap((outlet) => [
  {
    kind: "heading",
    text: `Patnam Pakodi – ${outlet.name}`,
    record_slug: outlet.slug,
  },
  {
    kind: "group",
    record_slug: outlet.slug,
    children: [
      {
        kind: "list",
        children: [
          { kind: "text", text: outlet.address },
          { kind: "link", text: outlet.phone, href: `tel:${outlet.phone}` },
          { kind: "text", text: outlet.hours },
        ],
      },
      { kind: "map", href: "" },
      { kind: "enquiry", text: "Directions" },
      { kind: "image", image: "/images/fixture.webp" },
    ],
  },
]);
function flatten(blocks) {
  return blocks.flatMap((block) => [block, ...flatten(block.children ?? [])]);
}
test("outlet unpublishing removes headings, cards, phone and map together", () => {
  const output = outletBlocks(blocks, outlets.slice(1));
  assert(!output.some((block) => block.record_slug === outlets[0].slug));
  assert.equal(output.filter((block) => block.record_slug).length, 2);
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
