"""Brand-scoped product discovery and deletion without losing order history."""

from fastapi import HTTPException
from psycopg.types.json import Jsonb

from app.commerce import audit
from app.security import one, rows


async def find_products(conn, *, q, mode, status, limit, offset):
    conditions, values = [], []
    if q.strip():
        conditions.append("strpos(lower(concat_ws(' ',sku,product->>'name')),lower(%s))>0")
        values.append(q.strip())
    if mode:
        conditions.append("COALESCE(product->>'mode','packaged')=%s")
        values.append(mode)
    if status:
        conditions.append("published=%s")
        values.append(status == "published")
    where = " AND ".join(conditions) or "true"
    count = await one(conn, "SELECT count(*) AS total FROM variants WHERE " + where, values)
    items = await rows(
        conn,
        "SELECT * FROM variants WHERE "
        + where
        + " ORDER BY lower(product->>'name'),sku,id LIMIT %s OFFSET %s",
        [*values, limit, offset],
    )
    return items, count["total"]


async def delete_product(conn, identifier, actor):
    # Checkout, editing and stock changes lock this same row through commit.
    product = await one(conn, "SELECT * FROM variants WHERE id=%s FOR UPDATE", (identifier,))
    if not product:
        raise HTTPException(404, "Product not found")
    if product["reserved"]:
        raise HTTPException(409, "This product has reserved stock. It cannot be deleted.")
    ordered = await one(
        conn,
        "SELECT EXISTS(SELECT 1 FROM orders WHERE lines @> %s) AS found",
        (Jsonb([{"variant_id": str(identifier)}]),),
    )
    if ordered["found"]:
        raise HTTPException(409, "This product has order history. Unpublish it to stop new orders.")
    # Keep the public content record and uploaded media; removal only hides the
    # product from sale. The append-only audit retains the deleted identity.
    await conn.execute(
        "UPDATE content_records SET published=false WHERE kind='product' AND slug=%s",
        (product["slug"],),
    )
    await conn.execute("DELETE FROM variants WHERE id=%s", (identifier,))
    await audit(
        conn,
        actor,
        "variant.deleted",
        identifier,
        {"sku": product["sku"], "slug": product["slug"], "stock": product["stock"]},
    )
