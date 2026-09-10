"""Read only published, schema-valid records; fail closed on malformed content."""

from fastapi import HTTPException
from psycopg import AsyncConnection

from app.schemas import FranchiseModel, MenuItem, Outlet, Page, Product, Storefront


async def storefront(connection: AsyncConnection) -> Storefront:
    cursor = await connection.execute(
        "SELECT kind, slug, payload FROM content_records "
        "WHERE published = true AND brand_id = %s ORDER BY position, slug",
        ("patnam-pakodi",),
    )
    records = await cursor.fetchall()
    by_kind: dict[str, list[dict]] = {}
    for record in records:
        by_kind.setdefault(record["kind"], []).append(record["payload"])
    brand = by_kind.get("brand", [])
    if not brand:
        raise HTTPException(503, "Content is temporarily unavailable")
    return Storefront(
        **brand[0],
        pages=[Page.model_validate(row) for row in by_kind.get("page", [])],
        menu=[MenuItem.model_validate(row) for row in by_kind.get("menu", [])],
        outlets=[Outlet.model_validate(row) for row in by_kind.get("outlet", [])],
        franchise_models=[
            FranchiseModel.model_validate(row) for row in by_kind.get("franchise", [])
        ],
        products=[Product.model_validate(row) for row in by_kind.get("product", [])],
    )
