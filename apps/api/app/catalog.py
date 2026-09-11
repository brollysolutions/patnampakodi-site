"""Public catalog search under the existing request-scoped RLS connection."""

from app.security import rows


async def search_catalog(
    conn, *, q="", category="", tag="", dietary="", max_price=None, sort="default", mode=""
):
    ordering = {
        "default": "slug",
        "price-asc": "price_paise,slug",
        "price-desc": "price_paise DESC,slug",
        "name": "lower(product->>'name'),slug",
    }[sort]
    conditions = ["published"]
    parameters = []
    if mode:
        conditions.append("COALESCE(product->>'mode','packaged')=%s")
        parameters.append(mode)
    if q.strip():
        conditions.append(
            "strpos(lower(concat_ws(' ',product->>'name',product->>'description')),lower(%s))>0"
        )
        parameters.append(q.strip())
    if category:
        conditions.append("product->>'category'=%s")
        parameters.append(category)
    if tag:
        conditions.append("COALESCE(product->'tags','[]'::jsonb) ? %s")
        parameters.append(tag)
    if dietary:
        conditions.append("product->>'dietary'=%s")
        parameters.append(dietary)
    if max_price is not None:
        conditions.append("price_paise<=%s")
        parameters.append(max_price)
    return await rows(
        conn,
        "SELECT * FROM variants WHERE " + " AND ".join(conditions) + " ORDER BY " + ordering,
        tuple(parameters),
    )
