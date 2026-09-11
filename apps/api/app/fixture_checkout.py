"""Local-only checkout simulation through the normal signed provider inbox."""

from datetime import UTC, datetime

import httpx
from fastapi import HTTPException

from app import commerce, providers
from app.config import fixture_mode
from app.security import one


async def capture_fixture(conn, order, quote_version):
    if not fixture_mode():
        raise HTTPException(404, "Not found")
    if order["quote_version"] != quote_version:
        raise HTTPException(409, "The delivery quote has changed")
    if order["status"] == "paid":
        return "Local test payment already confirmed"
    if (
        order["status"] != "payment_pending"
        or not order["reservation_active"]
        or not order["reserved_until"]
        or order["reserved_until"] <= datetime.now(UTC)
    ):
        raise HTTPException(409, "Start payment again to reserve the order")
    payment = await one(
        conn,
        "SELECT provider_order FROM payments WHERE order_id=%s "
        "AND quote_version=%s ORDER BY created_at DESC LIMIT 1",
        (order["id"], quote_version),
    )
    if not payment or not payment["provider_order"]:
        raise HTTPException(409, "Local payment setup is still running")
    try:
        await providers.fixture_request("POST", "orders/" + payment["provider_order"] + "/capture")
    except httpx.HTTPError as error:
        raise HTTPException(503, "Local payment fixture is temporarily unavailable") from error
    await commerce.audit(conn, "customer", "fixture.capture_requested", order["id"], {})
    return "Local test payment submitted. Refresh the order for confirmation."
