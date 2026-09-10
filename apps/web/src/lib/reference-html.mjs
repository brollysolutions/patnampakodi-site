/** Static editorial HTML: fixed tags/attributes, escaped text, no accepted HTML.
 * Keeping the content in one server-rendered fragment avoids hydrating hundreds
 * of inert layout nodes. Enquiry buttons use the single delegated dialog handler.
 * @typedef {import("../../../../packages/contracts/schema").components["schemas"]["ContentBlock"]} Block
 */

const escape = (value) =>
  String(value ?? "").replace(
    /[&<>"']/g,
    (character) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      })[character],
  );

function href(value) {
  const link = String(value ?? "");
  return !/[\\\x00-\x1f\x7f]/.test(link) &&
    /^(?:https:\/\/|mailto:|tel:|\/(?!\/))/.test(link)
    ? link
    : "";
}

/** @param {Block[]} blocks
 * @param {{menu: boolean, imageProps: (block: Block, priority: boolean) => Record<string, unknown>}} options
 */
export function referenceHtml(blocks, options) {
  /** @param {Block} block @param {boolean} priority @param {number} depth @returns {string} */
  function render(block, priority, depth) {
    const children = (block.children ?? [])
      .map((child) => render(child, priority, depth + 1))
      .join("");
    const link = href(block.href);
    switch (block.kind) {
      case "group": {
        const row = block.layout === "row";
        const article = options.menu && depth === 1;
        const tag = article ? "article" : "div";
        const tone = ["cream", "white", "brown"].includes(block.tone)
          ? block.tone
          : "none";
        const basis =
          Number.isFinite(block.basis) &&
          block.basis >= 10 &&
          block.basis <= 100
            ? block.basis
            : 100;
        return `<${tag} class="reference-group reference-${row ? "row" : "column"} tone-${tone}${block.card ? " reference-card" : ""}${article ? " menu-item" : ""}" style="flex-basis:${basis}%">${children}</${tag}>`;
      }
      case "heading": {
        const level = [1, 2, 3, 4].includes(block.level) ? block.level : 2;
        const text = escape(block.text);
        return `<h${level}>${link ? `<a href="${escape(link)}">${text}</a>` : text}</h${level}>`;
      }
      case "text":
        return `<div class="reference-copy">${String(block.text ?? "")
          .split(/\n\n+/)
          .map((text) => `<p>${escape(text)}</p>`)
          .join("")}</div>`;
      case "image": {
        if (!/^\/images\/live\/[a-z0-9-]+\.webp$/.test(block.image)) return "";
        const props = options.imageProps(block, priority);
        const attributes = [
          "src",
          "srcSet",
          "sizes",
          "width",
          "height",
          "loading",
          "fetchPriority",
          "decoding",
        ]
          .filter((key) => props[key] !== undefined)
          .map((key) => `${key.toLowerCase()}="${escape(props[key])}"`)
          .join(" ");
        return `<img class="reference-image" ${attributes} alt="${escape(block.alt)}">`;
      }
      case "list":
        return `<ul class="${block.items?.length === 1 ? "reference-label" : "reference-list"}">${(block.items ?? []).map((text) => `<li>${escape(text)}</li>`).join("")}${(
          block.children ?? []
        )
          .map((item) => {
            const target = href(item.href);
            return `<li>${target ? `<a href="${escape(target)}">${escape(item.text)}</a>` : escape(item.text)}</li>`;
          })
          .join("")}</ul>`;
      case "link":
        return link
          ? `<a class="button" href="${escape(link)}">${escape(block.text)}</a>`
          : `<p>${escape(block.text)}</p>`;
      case "enquiry":
        return `<button type="button" class="button" data-enquiry="${escape(block.text)}">${escape(block.text)}</button>`;
      case "faq":
        return `<details class="reference-faq"><summary>${escape(block.title)}</summary><p>${escape(block.text)}</p></details>`;
      case "icon":
        return `<span class="reference-icon" aria-hidden="true">${escape(block.text)}</span>`;
      case "map":
        return /^https:\/\/(?:maps\.google\.com|www\.google\.com)\//.test(link)
          ? `<iframe class="reference-map" title="${escape(block.title)}" src="${escape(link)}" loading="lazy" referrerpolicy="no-referrer"></iframe>`
          : link
            ? `<a class="button" href="${escape(link)}" target="_blank" rel="noopener noreferrer">${escape(block.title)}</a>`
            : "";
      default:
        return "";
    }
  }
  return blocks
    .map(
      (block, index) =>
        `<section class="reference-section container">${render(block, index === 0, 0)}</section>`,
    )
    .join("");
}
