import type { components } from "../../../../packages/contracts/schema";
import { StructuredPage } from "./StructuredPage";
import { SiteLink } from "./SiteLink";
import { filterOutlets } from "@/lib/policy.mjs";
import { menuBlocks, menuCategories } from "@/lib/reference-menu.mjs";
import { outletBlocks } from "@/lib/reference-outlets.mjs";
type Block = components["schemas"]["ContentBlock"];
type Outlet = components["schemas"]["Outlet"];

export function ReferenceDiscovery({
  blocks,
  slug,
  q,
  category,
  outlets,
  items,
}: {
  blocks: Block[];
  slug: string;
  q: string;
  category: string;
  outlets: Outlet[];
  items: components["schemas"]["MenuItem"][];
}) {
  const menu = slug === "menu";
  const { blocks: selected, count: matches } = menuBlocks(
    blocks,
    items,
    category,
    q,
  );
  const locations = filterOutlets(outlets, q) as Outlet[];
  return (
    <>
      <section className="container section discovery-controls">
        {menu ? <h1>Menu</h1> : <h1>Find Your Nearest Patnam Pakodi Branch</h1>}
        <form method="get" className="actions">
          {menu && category && (
            <input type="hidden" name="category" value={category} />
          )}
          <label className="field">
            {menu ? "Find your favourite" : "City, neighbourhood or pincode"}
            <input name="q" type="search" defaultValue={q} maxLength={100} />
          </label>
          <button className="button">{menu ? "Search" : "Find a store"}</button>
        </form>
        {menu && (
          <form method="get" className="actions" aria-label="Menu categories">
            {q && <input type="hidden" name="q" value={q} />}
            {menuCategories.map((name) => (
              <button
                className="button button-small"
                key={name}
                name="category"
                value={name}
                aria-pressed={category === name}
              >
                {name}
              </button>
            ))}
          </form>
        )}
      </section>
      {menu ? (
        matches ? (
          <StructuredPage
            slug={slug}
            blocks={selected.map((block) => ({
              ...block,
              children: block.children.map((child) =>
                child.level === 1 && child.kind === "heading"
                  ? { ...child, level: 2 as const }
                  : child,
              ),
            }))}
          />
        ) : (
          <section className="container section">
            <h2>No bites found.</h2>
            <SiteLink href="/menu/">Show the full menu</SiteLink>
          </section>
        )
      ) : q ? (
        <section className="container section">
          <div className="outlet-grid">
            {locations.map((outlet) => (
              <article className="panel" key={outlet.slug}>
                <h2>{outlet.name}</h2>
                <p>
                  {outlet.city} · {outlet.pincode}
                </p>
                {outlet.address && <p>{outlet.address}</p>}
                <a className="button" href={`/branches/${outlet.slug}/`}>
                  View branch
                </a>
              </article>
            ))}
          </div>
          {!locations.length && (
            <>
              <h2>Let’s try another neighbourhood.</h2>
              <SiteLink href="/branches/">Show all branches</SiteLink>
            </>
          )}
        </section>
      ) : (
        <StructuredPage
          slug={slug}
          blocks={outletBlocks(blocks, outlets).map((block) => demote(block))}
        />
      )}
    </>
  );
}
function demote(block: Block): Block {
  return {
    ...block,
    level: block.level === 1 ? 2 : block.level,
    children: block.children.map(demote),
  };
}
