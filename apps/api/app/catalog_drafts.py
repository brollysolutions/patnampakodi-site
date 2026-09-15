"""Prepare the saved food references for staff without inventing sale data."""

import json
from pathlib import Path

from app.commerce_schemas import CatalogDraft
from app.security import rows

CONTENT = Path(__file__).resolve().parents[1] / "content"
# The existing product URL names the same Pachi Mirchi menu flavour.
PRODUCT_SLUGS = {"pachi-mirchi-chicken-pakodi": "pachi-mirchi-kodi-pakodi"}


def source_catalog() -> list[CatalogDraft]:
    records = json.loads((CONTENT / "storefront.json").read_text(encoding="utf-8"))
    inventory = json.loads((CONTENT / "catalog-source-inventory.json").read_text(encoding="utf-8"))
    # Menu cards repeat generic pakodi artwork, even for drinks and dips. Only
    # the product-specific source inventory supplies automatic product images.
    drafts = {}
    for row in records:
        # These are private source observations, including the retired public menu.
        if row["kind"] != "menu":
            continue
        item = row["payload"]
        slug = PRODUCT_SLUGS.get(item["slug"], item["slug"])
        drafts[slug] = CatalogDraft(
            sku="PP-" + slug.upper(),
            slug=slug,
            name=item["name"],
            description=item.get("description", ""),
            mode="fresh",
            category=item["category"].lower(),
            dietary=item.get("dietary", "unconfirmed"),
            tags=[slug],
        )
    for item in inventory["products"]:
        slug = item["slug"]
        if slug in drafts:
            drafts[slug] = CatalogDraft.model_validate(
                {**drafts[slug].model_dump(), "image": item["local_image"]}
            )
            continue
        packaged = "ready-mix" in slug
        drafts[slug] = CatalogDraft(
            sku="PP-" + slug.upper(),
            slug=slug,
            name=item["title"],
            mode="packaged" if packaged else "fresh",
            category=item["category"],
            image=item["local_image"],
            tags=item["tags"],
        )
    return sorted(drafts.values(), key=lambda item: (item.mode, item.name.casefold()))


async def pending_catalog(conn) -> list[CatalogDraft]:
    # Use the normal request-scoped RLS connection; never overwrite an operator's SKU.
    existing = await rows(conn, "SELECT slug,sku FROM variants")
    slugs = {item["slug"] for item in existing}
    skus = {item["sku"] for item in existing}
    return [item for item in source_catalog() if item.slug not in slugs and item.sku not in skus]
