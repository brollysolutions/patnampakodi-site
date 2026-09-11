"""Server-priced checkout. No client price, brand or payment result is authoritative."""

import json
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from cryptography.fernet import InvalidToken
from fastapi import HTTPException
from psycopg.types.json import Jsonb

from app import commerce
from app.checkout_schemas import (
    CheckoutQuote,
    CheckoutQuoteRequest,
    FulfilmentSettings,
    Serviceability,
)
from app.commerce_schemas import BusinessSettings, CartLine
from app.config import BRAND
from app.security import digest, one, seal, unseal


def fingerprint(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")))


async def configuration(conn):
    row = await one(
        conn, "SELECT data FROM fulfilment_settings WHERE brand_id=%s FOR SHARE", (BRAND,)
    )
    return FulfilmentSettings.model_validate(row["data"] if row else {})


async def availability(conn, mode, pincode="", *, now=None):
    settings = await configuration(conn)
    result = Serviceability(
        mode=mode, available=False, message="Online ordering is being prepared."
    )
    if mode == "fresh":
        result.outlet_slug = settings.outlet_slug
        result.hours = settings.hours
        result.preparation_minutes = settings.preparation_minutes
        outlet = await one(
            conn,
            "SELECT payload FROM content_records WHERE kind='outlet' AND slug=%s AND published",
            (settings.outlet_slug,),
        )
        if outlet:
            result.outlet_name = outlet["payload"]["name"]
        if not settings.fresh_enabled or not outlet:
            return result
        if settings.fresh_paused:
            result.message = "The kitchen has paused online orders. Please check back shortly."
            return result
        local = (now or datetime.now(UTC)).astimezone(ZoneInfo("Asia/Kolkata"))
        if not any(
            window.day == local.weekday()
            and window.opens <= local.strftime("%H:%M") < window.closes
            for window in settings.hours
        ):
            result.message = (
                "The kitchen is closed. Browse the menu and order during opening hours."
            )
            return result
    elif not settings.packaged_enabled:
        return result
    if not pincode:
        result.message = "Enter your delivery PIN code to check availability."
        return result
    rule = next(
        (rule for rule in settings.rules if rule.mode == mode and rule.pincode == pincode), None
    )
    if not rule:
        result.message = "We don't deliver this range to that PIN code yet."
        return result
    result.available = True
    result.delivery_paise = rule.fee_paise
    result.state_code = rule.state_code
    result.message = "Delivery is available to your PIN code."
    return result


async def calculate(conn, payload):
    service = await availability(conn, payload.mode, payload.customer.pincode)
    if not service.available:
        raise HTTPException(409, service.message)
    if service.state_code != payload.customer.state_code:
        raise HTTPException(422, "The selected state does not match this delivery PIN code")
    row = await one(conn, "SELECT data FROM settings WHERE brand_id=%s FOR SHARE", (BRAND,))
    if not row:
        raise HTTPException(409, "Online checkout is not available yet")
    seller = BusinessSettings.model_validate(row["data"])
    if not seller.approved_for_sales or not seller.gstin.startswith(seller.state_code):
        raise HTTPException(409, "Online checkout is not available yet")
    lines = await commerce.snapshot(
        conn, payload.lines, mode=payload.mode, outlet_slug=service.outlet_slug, check_stock=True
    )
    delivery = service.delivery_paise
    total = sum(line["price_paise"] * line["quantity"] for line in lines) + delivery
    if total > 100000000:
        raise HTTPException(422, "Order total exceeds the supported limit")
    tax = sum(
        commerce.tax_amount(line["price_paise"] * line["quantity"], line["gst_bps"])
        for line in lines
    ) + commerce.tax_amount(delivery, seller.delivery_gst_bps)
    interstate = seller.state_code != payload.customer.state_code
    taxes = {
        "cgst": 0 if interstate else tax // 2,
        "sgst": 0 if interstate else tax - tax // 2,
        "igst": tax if interstate else 0,
        "taxable": total - tax,
    }
    values = {
        "lines": lines,
        "delivery_paise": delivery,
        "total_paise": total,
        "tax": taxes,
        "seller": seller.model_dump(mode="json"),
        "outlet_slug": service.outlet_slug,
    }
    return values, service


async def quote(conn, payload):
    values, service = await calculate(conn, payload)
    expires = datetime.now(UTC) + timedelta(minutes=15)
    token = seal(
        {
            "purpose": "checkout-quote-v1",
            "brand": BRAND,
            "request": fingerprint(payload.model_dump(mode="json")),
            "values": fingerprint(values),
            "expires": expires.timestamp(),
        }
    )
    return CheckoutQuote(
        quote_token=token,
        expires_at=expires,
        fulfilment=service,
        **{key: values[key] for key in ("lines", "delivery_paise", "total_paise", "tax")},
    )


async def create(conn, payload):
    key = digest(str(payload.request_key))
    await conn.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (key,))
    existing = await one(conn, "SELECT * FROM orders WHERE request_key=%s FOR UPDATE", (key,))
    if existing:
        if existing["request_hash"] != digest(
            json.dumps(payload.model_dump(mode="json"), sort_keys=True)
        ):
            raise HTTPException(409, "This checkout was already submitted with different details")
        return existing, await commerce.token_for(conn, existing["id"])
    request = CheckoutQuoteRequest(
        mode=payload.mode, customer=payload.customer, lines=payload.lines
    )
    try:
        proof = unseal(payload.quote_token)
        valid = (
            isinstance(proof, dict)
            and proof.get("purpose") == "checkout-quote-v1"
            and proof.get("brand") == BRAND
            and proof.get("request") == fingerprint(request.model_dump(mode="json"))
            and proof.get("expires", 0) > datetime.now(UTC).timestamp()
        )
    except (ValueError, TypeError, KeyError, InvalidToken):
        valid = False
    if not valid:
        raise HTTPException(409, "Your checkout review expired. Review the total again.")
    values, service = await calculate(conn, request)
    if proof.get("values") != fingerprint(values):
        raise HTTPException(
            409, "Prices or delivery changed. Review the updated total before paying."
        )
    order, token = await commerce.create_request(
        conn, payload, shopping_mode=payload.mode, outlet_slug=service.outlet_slug, instant=True
    )
    fulfilment = {"outlet_slug": service.outlet_slug, "outlet_name": service.outlet_name}
    if service.preparation_minutes is not None:
        fulfilment["preparation_minutes"] = service.preparation_minutes
    await conn.execute(
        "UPDATE orders SET fulfilment=%s WHERE id=%s", (Jsonb(fulfilment), order["id"])
    )
    await commerce.approve(conn, order["id"], values["delivery_paise"], "checkout", instant=True)
    await conn.execute(
        "UPDATE orders SET quote_expires_at=%s WHERE id=%s",
        (datetime.fromtimestamp(proof["expires"], UTC), order["id"]),
    )
    return await commerce.order_by_id(conn, order["id"]), token


async def validate_payment(conn, order):
    payload = CheckoutQuoteRequest(
        mode=order["shopping_mode"],
        customer=order["customer"],
        lines=[
            CartLine(variant_id=line["variant_id"], quantity=line["quantity"])
            for line in order["lines"]
        ],
    )
    values, service = await calculate(conn, payload)
    if any(
        values[key] != order[key]
        for key in ("lines", "delivery_paise", "total_paise", "tax", "seller")
    ) or service.outlet_slug != order["fulfilment"].get("outlet_slug", ""):
        raise HTTPException(
            409, "Checkout details changed. Return to your cart to review the total."
        )
