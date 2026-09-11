"use client";
import type { components } from "../../../../packages/contracts/schema";
type Block = components["schemas"]["ContentBlock"];

export function readBlocks(
  blocks: Block[],
  form: FormData,
  prefix = "block",
): Block[] {
  return blocks.map((block, index) => {
    const key = `${prefix}-${index}`;
    return {
      ...block,
      text: form.has(`${key}-text`)
        ? String(form.get(`${key}-text`))
        : block.text,
      title: form.has(`${key}-title`)
        ? String(form.get(`${key}-title`))
        : block.title,
      href: form.has(`${key}-href`)
        ? String(form.get(`${key}-href`))
        : block.href,
      alt: form.has(`${key}-alt`) ? String(form.get(`${key}-alt`)) : block.alt,
      items: form.has(`${key}-items`)
        ? String(form.get(`${key}-items`))
            .split("\n")
            .map((s) => s.trim())
            .filter(Boolean)
        : block.items,
      children: readBlocks(block.children ?? [], form, key),
    };
  });
}

export function BlockEditor({
  blocks,
  prefix = "block",
}: {
  blocks: Block[];
  prefix?: string;
}) {
  return (
    <>
      {blocks.map((block, index) => {
        const key = `${prefix}-${index}`;
        if (block.record_slug)
          return (
            <p className="editor-section" key={key}>
              This card uses the published menu or outlet record “
              {block.record_slug}”. Edit that record in its content category.
            </p>
          );
        if (block.kind === "group")
          return (
            <details className="editor-section" key={key}>
              <summary>
                Section {index + 1}:{" "}
                {block.children.find((child) => child.kind === "heading")
                  ?.text ?? "Content and layout"}
              </summary>
              <BlockEditor blocks={block.children} prefix={key} />
            </details>
          );
        return (
          <div className="form-stack editor-section" key={key}>
            {block.kind === "faq" && (
              <label className="field">
                Question
                <input
                  name={`${key}-title`}
                  defaultValue={block.title}
                  maxLength={300}
                />
              </label>
            )}
            {["heading", "text", "link", "enquiry", "faq"].includes(
              block.kind,
            ) && (
              <label className="field">
                {block.kind === "heading"
                  ? "Heading"
                  : block.kind === "faq"
                    ? "Answer"
                    : "Text"}
                <textarea
                  name={`${key}-text`}
                  defaultValue={block.text}
                  rows={block.kind === "text" || block.kind === "faq" ? 4 : 2}
                  maxLength={20000}
                />
              </label>
            )}
            {block.kind === "list" && (
              <label className="field">
                List (one item per line)
                <textarea
                  name={`${key}-items`}
                  defaultValue={(block.items ?? []).join("\n")}
                  rows={5}
                />
              </label>
            )}
            {block.kind === "list" && !!block.children?.length && (
              <BlockEditor blocks={block.children} prefix={key} />
            )}
            {(block.kind === "link" ||
              (block.kind === "heading" && block.href) ||
              block.kind === "map") && (
              <label className="field">
                Destination
                <input
                  name={`${key}-href`}
                  defaultValue={block.href}
                  maxLength={2000}
                />
              </label>
            )}
            {block.kind === "image" && (
              <label className="field">
                Image description
                <input
                  name={`${key}-alt`}
                  defaultValue={block.alt}
                  maxLength={300}
                />
              </label>
            )}
          </div>
        );
      })}
    </>
  );
}
