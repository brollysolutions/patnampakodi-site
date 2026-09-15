"""Commerce transitions. Callers own a scoped transaction, not financial truth."""

import json
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException
from psycopg.types.json import Jsonb

from app.commerce_schemas import BusinessSettings, OrderView, QuoteLine
from app.config import BRAND
from app.ordering import require_ordering
from app.security import digest, one, random_token, seal


async def audit(conn, actor, action, entity, changes):
    await conn.execute(
        """
INSERT INTO audit_events(brand_id,actor,action,entity,changes)
VALUES(%s,%s,%s,%s,%s)
""",
        (BRAND, actor, action, str(entity), Jsonb(changes)),
    )


async def enqueue(conn, kind, key, payload, order_id=None):
    await conn.execute(
        """INSERT INTO outbox(id,brand_id,kind,event_key,payload,order_id)
      VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(event_key) DO NOTHING""",
        (uuid.uuid4(), BRAND, kind, key, seal(payload), order_id),
    )


async def token_for(conn, order_id):
    token = random_token()
    await conn.execute(
        """
INSERT INTO order_tokens(id,brand_id,order_id,expires_at)
SELECT %s,%s,id,LEAST(now()+interval '180 days',
COALESCE(delivered_at+interval '90 days',now()+interval '180 days'))
FROM orders WHERE id=%s
""",
        (digest(token), BRAND, order_id),
    )
    return token


async def notify(conn, order, event):
    if not order["consent"]:
        return
    token = await token_for(conn, order["id"])
    await enqueue(
        conn,
        "whatsapp",
        f"order:{order['id']}:{event}",
        {
            "phone": order["customer"]["phone"],
            "template": "order_update_v1",
            "parameters": [order["reference"], event.replace("_", " "), token],
        },
        order["id"],
    )


async def order_by_id(conn, order_id, lock=True):
    order = await one(
        conn, "SELECT * FROM orders WHERE id=%s" + (" FOR UPDATE" if lock else ""), (order_id,)
    )
    if not order:
        raise HTTPException(404, "Order not found")
    return order


async def order_by_token(conn, token, lock=True):
    found = await one(
        conn,
        """
SELECT order_id FROM order_tokens WHERE id=%s AND NOT revoked AND
expires_at>now()
""",
        (digest(token),),
    )
    if not found:
        raise HTTPException(404, "Order link is unavailable. Contact support for help.")
    return await order_by_id(conn, found["order_id"], lock)


def view(order):
    return OrderView.model_validate({key: order[key] for key in OrderView.model_fields})


async def snapshot(conn, requested, *, mode="packaged", outlet_slug="", check_stock=False):
    identifiers = [str(line.variant_id) for line in requested]
    if len(set(identifiers)) != len(identifiers):
        raise HTTPException(422, "Combine quantities for each product")
    result = []
    for line in sorted(requested, key=lambda item: str(item.variant_id)):
        variant = await one(
            conn, "SELECT * FROM variants WHERE id=%s AND published FOR UPDATE", (line.variant_id,)
        )
        if not variant:
            raise HTTPException(409, "A product is no longer available")
        product = variant["product"]
        if product.get("mode", "packaged") != mode or (
            mode == "fresh" and product.get("outlet_slug") != outlet_slug
        ):
            raise HTTPException(409, "Keep fresh and packaged products in their separate carts")
        if check_stock and variant["stock"] - variant["reserved"] < line.quantity:
            raise HTTPException(409, "Stock changed. Review your cart before paying.")
        result.append(
            QuoteLine(
                variant_id=line.variant_id,
                quantity=line.quantity,
                sku=variant["sku"],
                name=variant["product"]["name"],
                price_paise=variant["price_paise"],
                gst_bps=variant["gst_bps"],
                hsn=variant["hsn"],
            ).model_dump(mode="json")
        )
    return result


async def create_request(conn, payload, *, shopping_mode="packaged", outlet_slug="", instant=False):
    require_ordering()
    data = payload.model_dump(mode="json")
    request_hash = digest(json.dumps(data, sort_keys=True))
    key = digest(str(payload.request_key))
    # Serialize identical request keys before reading or inserting.
    await conn.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (key,))
    existing = await one(conn, "SELECT * FROM orders WHERE request_key=%s", (key,))
    if existing:
        if existing["request_hash"] != request_hash:
            raise HTTPException(
                409, "This request has already been submitted with different details"
            )
        return existing, await token_for(conn, existing["id"])
    lines = await snapshot(conn, payload.lines, mode=shopping_mode, outlet_slug=outlet_slug)
    identifier = uuid.uuid4()
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    reference = "PP-" + "".join(secrets.choice(alphabet) for _ in range(10))
    order = await one(
        conn,
        """
INSERT INTO
orders(id,brand_id,reference,request_key,request_hash,customer,lines,consent,consent_version,
shopping_mode,checkout_kind)
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'order-updates-2026-09',%s,%s) RETURNING *
""",
        (
            identifier,
            BRAND,
            reference,
            key,
            request_hash,
            Jsonb(data["customer"]),
            Jsonb(lines),
            payload.whatsapp_consent,
            shopping_mode,
            "instant" if instant else "staff",
        ),
    )
    await audit(conn, "customer", "request.created", identifier, {"status": "requested"})
    return order, await token_for(conn, identifier)


def tax_amount(gross, rate):
    return int(
        (Decimal(gross) * rate / (10000 + rate)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )


async def approve(conn, order_id, delivery, actor, *, instant=False):
    order = await order_by_id(conn, order_id)
    if order["checkout_kind"] == "instant" and not instant:
        raise HTTPException(409, "Instant checkout totals are calculated at checkout")
    if order["status"] not in {"requested", "approved"}:
        raise HTTPException(409, "Only unpaid requests can be approved")
    record = await one(conn, "SELECT data FROM settings WHERE brand_id=%s", (BRAND,))
    if not record:
        raise HTTPException(409, "Configure approved seller and tax details first")
    seller = BusinessSettings.model_validate(record["data"])
    if not seller.approved_for_sales or not seller.gstin.startswith(seller.state_code):
        raise HTTPException(409, "Approved seller and tax details are required")
    from app.commerce_schemas import CartLine

    lines = await snapshot(
        conn,
        [
            CartLine(variant_id=line["variant_id"], quantity=line["quantity"])
            for line in order["lines"]
        ],
        mode=order["shopping_mode"],
        outlet_slug=order["fulfilment"].get("outlet_slug", ""),
    )
    total = sum(line["price_paise"] * line["quantity"] for line in lines) + delivery
    if total > 100000000:
        raise HTTPException(422, "Order total exceeds the supported limit")
    tax = sum(
        tax_amount(line["price_paise"] * line["quantity"], line["gst_bps"]) for line in lines
    ) + tax_amount(delivery, seller.delivery_gst_bps)
    interstate = seller.state_code != order["customer"]["state_code"]
    taxes = {
        "cgst": 0 if interstate else tax // 2,
        "sgst": 0 if interstate else tax - tax // 2,
        "igst": tax if interstate else 0,
        "taxable": total - tax,
    }
    updated = await one(
        conn,
        """
UPDATE orders SET
status='approved',lines=%s,delivery_paise=%s,total_paise=%s,tax=%s,
seller=%s,quote_version=quote_version+1,quote_expires_at=now()+interval '24
hours',updated_at=now()
WHERE id=%s RETURNING *
""",
        (Jsonb(lines), delivery, total, Jsonb(taxes), Jsonb(seller.model_dump()), order_id),
    )
    await audit(
        conn,
        actor,
        "quote.approved",
        order_id,
        {
            "previous_total": order["total_paise"],
            "total": total,
            "version": updated["quote_version"],
        },
    )
    if not instant:
        await notify(conn, updated, "approved_" + str(updated["quote_version"]))
    return updated


async def release_stock(conn, order):
    if not order["reservation_active"]:
        return
    for line in sorted(order["lines"], key=lambda item: item["variant_id"]):
        await conn.execute(
            "UPDATE variants SET reserved=reserved-%s WHERE id=%s",
            (line["quantity"], line["variant_id"]),
        )
    await conn.execute(
        "UPDATE orders SET reservation_active=false,reserved_until=NULL WHERE id=%s", (order["id"],)
    )
    order["reservation_active"] = False


async def reserve(conn, order):
    for line in sorted(order["lines"], key=lambda item: item["variant_id"]):
        changed = await one(
            conn,
            """UPDATE variants SET reserved=reserved+%s
          WHERE id=%s AND published AND stock-reserved>=%s RETURNING id""",
            (line["quantity"], line["variant_id"], line["quantity"]),
        )
        if not changed:
            raise HTTPException(409, "Stock changed. Review your cart before paying.")
    await conn.execute(
        """
UPDATE orders SET reservation_active=true,reserved_until=now()+interval '15
minutes' WHERE id=%s
""",
        (order["id"],),
    )


async def begin_payment(conn, order, version):
    require_ordering()
    if order["status"] == "payment_pending":
        pending = await one(
            conn,
            "SELECT * FROM payments WHERE order_id=%s ORDER BY created_at DESC LIMIT 1",
            (order["id"],),
        )
        if pending and order["reserved_until"] and order["reserved_until"] > datetime.now(UTC):
            return pending
        raise HTTPException(409, "We are checking the previous payment. Please try again shortly.")
    if (
        order["status"] != "approved"
        or order["quote_version"] != version
        or order["quote_expires_at"] <= datetime.now(UTC)
    ):
        raise HTTPException(
            409,
            "The checkout review expired. Return to your cart to review the total."
            if order["checkout_kind"] == "instant"
            else "The quote is unavailable or expired. Ask staff to confirm it again.",
        )
    if order["checkout_kind"] == "instant":
        from app.checkout import validate_payment

        await validate_payment(conn, order)
    await reserve(conn, order)
    payment = await one(
        conn,
        """INSERT INTO payments(id,brand_id,order_id,quote_version,amount)
      VALUES(%s,%s,%s,%s,%s) RETURNING *""",
        (uuid.uuid4(), BRAND, order["id"], version, order["total_paise"]),
    )
    await conn.execute(
        "UPDATE orders SET status='payment_pending',updated_at=now() WHERE id=%s", (order["id"],)
    )
    await enqueue(
        conn,
        "create_payment",
        "payment:" + str(payment["id"]),
        {"payment_id": str(payment["id"])},
        order["id"],
    )
    return payment


async def refund(conn, order, amount, reason, actor, payment_id=None):
    payment = await one(
        conn,
        "SELECT * FROM payments WHERE id=%s AND order_id=%s AND status='captured' FOR UPDATE",
        (payment_id or order["primary_payment_id"], order["id"]),
    )
    if not payment:
        raise HTTPException(409, "No captured payment is available")
    used = await one(
        conn,
        """
SELECT COALESCE(sum(amount),0) AS amount FROM refunds WHERE payment_id=%s
AND status!='failed'
""",
        (payment["id"],),
    )
    if amount > payment["amount"] - used["amount"]:
        raise HTTPException(409, "Refund exceeds the remaining captured amount")
    identifier = uuid.uuid4()
    await conn.execute(
        """
INSERT INTO refunds(id,brand_id,payment_id,order_id,amount,reason)
VALUES(%s,%s,%s,%s,%s,%s)
""",
        (identifier, BRAND, payment["id"], order["id"], amount, reason),
    )
    await enqueue(
        conn, "refund", "refund:" + str(identifier), {"refund_id": str(identifier)}, order["id"]
    )
    await audit(conn, actor, "refund.requested", order["id"], {"amount": amount, "reason": reason})
    return identifier


async def cancel(conn, order, actor, *, allow_preparing=False):
    if order["status"] in {"cancelled", "refund_pending", "refunded", "declined"}:
        return order
    preparing = order["status"] == "preparing" and order["shopping_mode"] == "fresh"
    if order["status"] not in {"requested", "approved", "payment_pending", "paid"} and not (
        allow_preparing and preparing
    ):
        raise HTTPException(409, "Preparation or delivery has started. Contact support for help.")
    await release_stock(conn, order)
    if order["status"] == "paid":
        # Captured stock is returned only for this serialized physical cancellation.
        for line in sorted(order["lines"], key=lambda item: item["variant_id"]):
            await conn.execute(
                "UPDATE variants SET stock=stock+%s WHERE id=%s",
                (line["quantity"], line["variant_id"]),
            )
    if order["status"] == "paid" or preparing:
        # Food already being prepared is not automatically returned to sellable stock.
        used = await one(
            conn,
            "SELECT COALESCE(sum(amount),0) AS amount, "
            "COALESCE(sum(amount) FILTER (WHERE status='processed'),0) AS processed FROM refunds "
            "WHERE payment_id=%s AND status!='failed'",
            (order["primary_payment_id"],),
        )
        remaining = order["total_paise"] - used["amount"]
        if remaining:
            await refund(
                conn,
                order,
                remaining,
                "Staff cancellation during preparation"
                if preparing
                else "Pre-dispatch cancellation",
                actor,
            )
        status = "refunded" if used["processed"] == order["total_paise"] else "refund_pending"
    else:
        status = "cancelled"
    updated = await one(
        conn,
        "UPDATE orders SET status=%s,updated_at=now() WHERE id=%s RETURNING *",
        (status, order["id"]),
    )
    await audit(
        conn, actor, "order.cancelled", order["id"], {"before": order["status"], "after": status}
    )
    await notify(conn, updated, "cancelled")
    return updated


async def set_status(conn, order_id, change, actor):
    order = await order_by_id(conn, order_id)
    allowed = {
        "declined": {"requested", "approved"},
        "preparing": {"paid"} if order["shopping_mode"] == "fresh" else set(),
        "dispatched": {"preparing"} if order["shopping_mode"] == "fresh" else {"paid"},
        "delivered": {"dispatched", "delivery_issue"},
        "delivery_issue": {"dispatched"},
    }
    if order["status"] == change.status:
        return order
    if order["status"] not in allowed[change.status]:
        raise HTTPException(409, "This status change is not available")
    updated = await one(
        conn,
        """
UPDATE orders SET status=%s,note=%s,updated_at=now(),
delivered_at=CASE WHEN %s='delivered' THEN now() ELSE delivered_at END WHERE
id=%s RETURNING *
""",
        (change.status, change.note, change.status, order_id),
    )
    if change.status == "delivered":
        await conn.execute(
            """
UPDATE order_tokens SET expires_at=LEAST(expires_at,now()+interval '90
days') WHERE order_id=%s
""",
            (order_id,),
        )
    await audit(
        conn,
        actor,
        "order.status",
        order_id,
        {"before": order["status"], "after": change.status, "note": change.note},
    )
    await notify(conn, updated, change.status)
    return updated


async def captured(conn, entity):
    payment = await one(
        conn, "SELECT * FROM payments WHERE provider_order=%s", (entity.get("order_id", ""),)
    )
    if not payment:
        return
    order = await order_by_id(conn, payment["order_id"])
    payment = await one(conn, "SELECT * FROM payments WHERE id=%s FOR UPDATE", (payment["id"],))
    if (
        entity.get("currency") != "INR"
        or entity.get("amount") != payment["amount"]
        or entity.get("status") != "captured"
    ):
        raise ValueError("Provider payment does not match the stored order")
    if payment["status"] == "captured":
        return
    await conn.execute(
        """
UPDATE payments SET status='captured',provider_payment=%s,updated_at=now()
WHERE id=%s
""",
        (entity["id"], payment["id"]),
    )
    fulfill = (
        order["status"] in {"payment_pending", "approved"}
        and order["quote_version"] == payment["quote_version"]
        and order["primary_payment_id"] is None
    )
    if fulfill and not order["reservation_active"]:
        try:
            async with conn.transaction():
                await reserve(conn, order)
            order["reservation_active"] = True
        except HTTPException:
            fulfill = False
    if not fulfill:
        await refund(
            conn,
            order,
            payment["amount"],
            "Payment arrived after order became unavailable",
            "provider",
            payment["id"],
        )
        # An obsolete or second capture must never disturb a newer quote or a
        # fulfilled order. Only a cancelled/unfulfillable current attempt owns
        # the visible refund lifecycle.
        if not order["primary_payment_id"] and (
            order["status"] in {"cancelled", "declined"}
            or order["quote_version"] == payment["quote_version"]
        ):
            await release_stock(conn, order)
            await conn.execute(
                "UPDATE orders SET status='refund_pending',primary_payment_id=%s,"
                "updated_at=now() WHERE id=%s",
                (payment["id"], order["id"]),
            )
        return
    for line in sorted(order["lines"], key=lambda item: item["variant_id"]):
        await conn.execute(
            "UPDATE variants SET stock=stock-%s,reserved=reserved-%s WHERE id=%s",
            (line["quantity"], line["quantity"], line["variant_id"]),
        )
    date = datetime.now(UTC) + timedelta(hours=5, minutes=30)
    year = date.year if date.month >= 4 else date.year - 1
    period = str(year)[-2:] + str(year + 1)[-2:]
    sequence = await one(
        conn,
        """
INSERT INTO invoice_counters(brand_id,period,value) VALUES(%s,%s,1)
ON CONFLICT(brand_id,period) DO UPDATE SET value=invoice_counters.value+1
RETURNING value
""",
        (BRAND, period),
    )
    invoice = f"{order['seller']['invoice_prefix']}/{period}/{sequence['value']:06}"
    updated = await one(
        conn,
        """UPDATE orders SET status='paid',reservation_active=false,reserved_until=NULL,
      invoice_number=%s,primary_payment_id=%s,invoiced_at=now(),updated_at=now()
      WHERE id=%s RETURNING *""",
        (invoice, payment["id"], order["id"]),
    )
    await audit(
        conn,
        "provider",
        "payment.captured",
        order["id"],
        {"amount": payment["amount"], "invoice": invoice},
    )
    await notify(conn, updated, "paid")


async def refund_event(conn, entity):
    record = await one(
        conn,
        "SELECT * FROM refunds WHERE provider_id=%s OR id::text=%s",
        (entity.get("id", ""), entity.get("receipt", "")),
    )
    if not record:
        return
    order = await order_by_id(conn, record["order_id"])
    payment = await one(conn, "SELECT * FROM payments WHERE id=%s", (record["payment_id"],))
    if (
        entity.get("amount") != record["amount"]
        or entity.get("payment_id") != payment["provider_payment"]
    ):
        raise ValueError("Refund mismatch")
    if record["status"] == "processed":
        return
    status = entity.get("status")
    if status not in {"processed", "failed", "pending"}:
        return
    await conn.execute(
        "UPDATE refunds SET provider_id=%s,status=%s WHERE id=%s",
        (entity["id"], status, record["id"]),
    )
    if status == "processed":
        total = await one(
            conn,
            """
SELECT COALESCE(sum(amount),0) AS amount FROM refunds WHERE payment_id=%s AND
status='processed'
""",
            (order["primary_payment_id"],),
        )
        if (
            record["payment_id"] == order["primary_payment_id"]
            and total["amount"] == payment["amount"]
            and order["status"] == "refund_pending"
        ):
            await conn.execute(
                "UPDATE orders SET status='refunded',updated_at=now() WHERE id=%s", (order["id"],)
            )
        await notify(conn, order, "refund_processed_" + str(record["id"]))
    await audit(conn, "provider", "refund." + status, order["id"], {"amount": record["amount"]})
