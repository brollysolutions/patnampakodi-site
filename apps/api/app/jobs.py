"""One scheduler process; leased PostgreSQL outbox and verified reconciliation."""

import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from psycopg.types.json import Jsonb

from app import commerce, providers
from app.config import BRAND, validate_runtime
from app.security import connection, one, rows, unseal


async def dispatch(job):
    payload = unseal(job["payload"])
    if job["kind"] == "whatsapp":
        # Recheck opt-out after claiming, immediately before any provider call.
        if job["order_id"]:
            async with connection() as conn:
                order = await commerce.order_by_id(conn, job["order_id"], False)
            if not order["consent"]:
                return "suppressed"
        return await providers.send_whatsapp(payload)
    if job["kind"] == "create_payment":
        async with connection() as conn:
            payment = await one(
                conn, "SELECT * FROM payments WHERE id=%s", (payload["payment_id"],)
            )
            order = await commerce.order_by_id(conn, payment["order_id"], False)
        if payment["provider_order"]:
            return payment["provider_order"]
        if order["status"] != "payment_pending":
            return "suppressed"
        receipt = str(payment["id"])
        found = await providers.razorpay("GET", "orders", params={"receipt": receipt, "count": 100})
        matches = [item for item in found.get("items", []) if item.get("receipt") == receipt]
        if matches:
            provider_order = matches[0]
        elif payment["post_started"]:
            # A prior POST may have committed without returning; never blindly duplicate it.
            raise RuntimeError("Payment creation needs provider reconciliation")
        else:
            async with connection() as conn:
                claimed = await one(
                    conn,
                    "UPDATE payments SET post_started=true WHERE id=%s "
                    "AND NOT post_started RETURNING id",
                    (payment["id"],),
                )
            if not claimed:
                raise RuntimeError("Payment creation needs provider reconciliation")
            provider_order = await providers.razorpay(
                "POST",
                "orders",
                json={"amount": payment["amount"], "currency": "INR", "receipt": receipt},
            )
        if provider_order["amount"] != payment["amount"] or provider_order["currency"] != "INR":
            raise ValueError("Provider order mismatch")
        async with connection() as conn:
            await conn.execute(
                """
UPDATE payments SET provider_order=%s,status='created',updated_at=now()
WHERE id=%s AND provider_order IS NULL
""",
                (provider_order["id"], payment["id"]),
            )
        return provider_order["id"]
    if job["kind"] == "refund":
        async with connection() as conn:
            record = await one(
                conn,
                """
SELECT r.*,p.provider_payment FROM refunds r JOIN payments p ON
p.id=r.payment_id WHERE r.id=%s
""",
                (payload["refund_id"],),
            )
        if record["status"] == "processed":
            return record["provider_id"]
        result = await providers.razorpay(
            "POST",
            f"payments/{record['provider_payment']}/refund",
            headers={"X-Refund-Idempotency": str(record["id"])},
            json={"amount": record["amount"], "speed": "normal", "receipt": str(record["id"])},
        )
        async with connection() as conn:
            await commerce.refund_event(conn, result)
        return result["id"]
    if job["kind"] == "razorpay_event":
        async with connection() as conn:
            event = await one(
                conn, "SELECT * FROM provider_events WHERE id=%s FOR UPDATE", (payload["event_id"],)
            )
            if event["processed"]:
                return "processed"
            data = unseal(event["payload"])
            if data["event"] == "payment.captured":
                await commerce.captured(conn, data["payload"]["payment"]["entity"])
            elif data["event"].startswith("refund."):
                await commerce.refund_event(conn, data["payload"]["refund"]["entity"])
            await conn.execute(
                "UPDATE provider_events SET processed=true WHERE id=%s", (event["id"],)
            )
        return "processed"
    raise ValueError("Unknown job type")


async def run_once():
    await check_health("worker", "running")
    for _ in range(20):
        lease = uuid.uuid4()
        async with connection() as conn:
            job = await one(
                conn,
                """
UPDATE outbox SET status='processing',attempts=attempts+1,
lease_until=now()+interval '2 minutes',lease_id=%s WHERE id=(SELECT id FROM
outbox
WHERE (status='pending' AND due_at<=now()) OR (status='processing' AND
lease_until<now())
ORDER BY due_at FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *
""",
                (lease,),
            )
        if not job:
            break
        try:
            provider_id = await dispatch(job)
            status = "suppressed" if provider_id == "suppressed" else "sent"
            async with connection() as conn:
                await conn.execute(
                    """
UPDATE outbox SET status=CASE WHEN status='delivered' THEN status ELSE %s END,
provider_id=%s,last_error='',lease_until=NULL
WHERE id=%s AND lease_id=%s
""",
                    (status, provider_id, job["id"], lease),
                )
                await apply_receipts(conn)
        except Exception as error:
            # Persist only exception class, never provider response bodies or customer data.
            exhausted = job["attempts"] >= 5
            delay = (60, 300, 1800, 7200)[min(job["attempts"] - 1, 3)]
            async with connection() as conn:
                await conn.execute(
                    """UPDATE outbox SET status=%s,last_error=%s,due_at=%s,lease_until=NULL
                  WHERE id=%s AND lease_id=%s""",
                    (
                        "failed" if exhausted else "pending",
                        type(error).__name__,
                        datetime.now(UTC) + timedelta(seconds=delay),
                        job["id"],
                        lease,
                    ),
                )


async def apply_receipts(conn):
    await conn.execute("""
      UPDATE outbox o SET status=r.status,
      delivered_at=CASE WHEN r.status='delivered' THEN r.received_at ELSE o.delivered_at END,
      last_error=CASE WHEN r.status='failed' THEN 'ProviderDeliveryFailed' ELSE '' END
      FROM message_receipts r WHERE o.provider_id=r.id AND o.kind='whatsapp'
      AND o.status!='delivered'
    """)


async def maintenance():
    async with connection() as conn:
        await apply_receipts(conn)
        expired = await rows(
            conn,
            """
SELECT * FROM orders WHERE reservation_active AND reserved_until<now() ORDER
BY id FOR UPDATE SKIP LOCKED
""",
        )
        for order in expired:
            await commerce.release_stock(conn, order)
            await conn.execute(
                """
UPDATE orders SET status='approved',updated_at=now() WHERE id=%s AND
status='payment_pending'
""",
                (order["id"],),
            )
        # Raw event bodies are encrypted; discard processed payloads after seven days.
        await conn.execute(
            """
UPDATE provider_events SET payload='' WHERE processed AND
created_at<now()-interval '7 days' AND payload!=''
"""
        )
        await conn.execute(
            """
UPDATE outbox SET payload='' WHERE status IN ('delivered','suppressed') AND
created_at<now()-interval '7 days' AND payload!=''
"""
        )


async def reconcile():
    async with connection() as conn:
        payments = await rows(
            conn,
            """
SELECT * FROM payments WHERE provider_order IS NOT NULL AND
status!='captured' ORDER BY updated_at LIMIT 100
""",
        )
    for payment in payments:
        try:
            data = await providers.razorpay("GET", f"orders/{payment['provider_order']}/payments")
            async with connection() as conn:
                for entity in data.get("items", []):
                    if entity.get("status") == "captured":
                        await commerce.captured(conn, entity)
                await conn.execute(
                    "UPDATE payments SET updated_at=now() WHERE id=%s", (payment["id"],)
                )
        except Exception:
            continue  # Per-record failure must not prevent recovery of other payments.
    async with connection() as conn:
        refunds = await rows(
            conn,
            """
SELECT * FROM refunds WHERE provider_id IS NOT NULL AND status='pending'
LIMIT 100
""",
        )
    for refund in refunds:
        try:
            data = await providers.razorpay("GET", "refunds/" + refund["provider_id"])
            async with connection() as conn:
                await commerce.refund_event(conn, data)
        except Exception:
            continue


async def check_health(name, status):
    async with connection() as conn:
        await conn.execute(
            "INSERT INTO operation_checks(brand_id,name,status) VALUES(%s,%s,%s) "
            "ON CONFLICT(brand_id,name) DO UPDATE SET status=excluded.status,checked_at=now()",
            (BRAND, name, status),
        )


async def settlements():
    try:
        today = datetime.now(UTC) + timedelta(hours=5, minutes=30)
        prior = today.replace(day=1) - timedelta(days=1)
        for period in (prior, today):
            for offset in range(0, 50000, 1000):
                data = await providers.razorpay(
                    "GET",
                    "settlements/recon/combined",
                    params={
                        "year": period.year,
                        "month": period.month,
                        "count": 1000,
                        "skip": offset,
                    },
                )
                async with connection() as conn:
                    for item in data.get("items", []):
                        # Discard card/bank details from provider reconciliation reports.
                        safe = {
                            key: item.get(key)
                            for key in (
                                "entity_id",
                                "type",
                                "amount",
                                "currency",
                                "fee",
                                "tax",
                                "settlement_id",
                            )
                        }
                        await conn.execute(
                            "INSERT INTO settlements(id,brand_id,payload) VALUES(%s,%s,%s) "
                            "ON CONFLICT(id) DO UPDATE SET "
                            "payload=excluded.payload,fetched_at=now()",
                            (safe["entity_id"], BRAND, Jsonb(safe)),
                        )
                if len(data.get("items", [])) < 1000:
                    break
            else:
                raise RuntimeError("Reconciliation requires a narrower operator export")
        await check_health("settlements", "ok")
    except Exception:
        await check_health("settlements", "unavailable")


async def main():
    validate_runtime()
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(run_once, "interval", seconds=2, max_instances=1, coalesce=True)
    scheduler.add_job(maintenance, "interval", seconds=30, max_instances=1, coalesce=True)
    scheduler.add_job(reconcile, "interval", minutes=2, max_instances=1, coalesce=True)
    scheduler.add_job(
        settlements,
        "interval",
        hours=24,
        max_instances=1,
        coalesce=True,
        next_run_time=datetime.now(UTC),
    )
    scheduler.start()
    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)


async def singleton():
    async with connection() as conn:
        owned = await one(conn, "SELECT pg_try_advisory_lock(771802611) AS owned")
        await conn.commit()
        if not owned["owned"]:
            raise RuntimeError("Another scheduler owns this database")
        await main()


if __name__ == "__main__":
    import sys

    with asyncio.Runner(
        loop_factory=asyncio.SelectorEventLoop if sys.platform == "win32" else None
    ) as runner:
        runner.run(singleton())
