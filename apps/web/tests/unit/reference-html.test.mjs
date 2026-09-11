import test from "node:test";
import assert from "node:assert/strict";
import { referenceHtml } from "../../src/lib/reference-html.mjs";

const options = {
  menu: false,
  imageProps: (block) => ({
    src: block.image,
    width: 800,
    height: 600,
    loading: "lazy",
  }),
};
test("editorial strings cannot introduce tags, event attributes or unsafe destinations", () => {
  const attack = '\"><script>alert(1)</script><img src=x onerror="alert(2)"> &';
  const html = referenceHtml(
    [
      { kind: "heading", text: attack, level: 1, href: "javascript:alert(1)" },
      { kind: "text", text: attack },
      { kind: "faq", title: attack, text: attack },
      { kind: "enquiry", text: attack },
      {
        kind: "list",
        items: [attack],
        children: [{ text: attack, href: "//attacker.invalid" }],
      },
      {
        kind: "map",
        title: attack,
        href: 'https://maps.google.com/\" onload=\"alert(1)',
      },
      { kind: "image", image: "/images/live/example.webp", alt: attack },
    ],
    options,
  );
  assert(!html.includes("<script>"));
  assert(!html.includes("<img src=x"));
  assert(!html.includes('href="javascript:'));
  assert(!html.includes('href="//'));
  assert(!html.includes('src="https://maps.google.com/" onload='));
  assert(html.includes("&lt;script&gt;"));
  assert(html.includes('data-enquiry="&quot;&gt;'));
});

test("fixed tag and image allowlists reject executable or external editorial data", () => {
  const html = referenceHtml(
    [
      { kind: "script", text: "alert(1)" },
      { kind: "image", image: "https://attacker.invalid/pixel.png" },
      { kind: "heading", text: "Safe heading", level: "1 onclick=alert(1)" },
      { kind: "link", href: "/\\attacker.invalid", text: "Safe text" },
      {
        kind: "map",
        href: "https://maps.google.com.attacker.invalid/",
        title: "Map link",
      },
    ],
    options,
  );
  assert(!html.includes("<script"));
  assert(!html.includes("<img"));
  assert(!html.includes("<iframe"));
  assert(!html.includes("onclick"));
  assert(html.includes("<h2>Safe heading</h2>"));
  assert(html.includes("<p>Safe text</p>"));
});

test("FAQs, semantic menus, links and image dimensions are present in initial HTML", () => {
  const html = referenceHtml(
    [
      {
        kind: "group",
        layout: "row",
        children: [
          {
            kind: "group",
            children: [
              { kind: "heading", level: 3, text: "A dish", href: "/menu/" },
              {
                kind: "image",
                image: "/images/live/example.webp",
                alt: "Dish",
              },
              {
                kind: "faq",
                title: "Question?",
                text: "Readable without JavaScript.",
              },
            ],
          },
        ],
      },
    ],
    { ...options, menu: true },
  );
  assert(html.includes("<article"));
  assert(html.includes('<h3><a href="/menu/">A dish</a></h3>'));
  assert(html.includes('width="800" height="600" loading="lazy"'));
  assert(
    html.includes(
      "<summary>Question?</summary><p>Readable without JavaScript.</p>",
    ),
  );
  assert(!html.includes("hidden"));
});
