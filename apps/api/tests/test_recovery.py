"""Regression tests for independently captured attempts and delivery races."""

import uuid

import psycopg
import pytest
from conftest import OWNER, require_fixture_environment
from test_commerce import (
    approved,
    capture,
    run,
    start_payment,
)

from app import commerce, jobs
from app.config import BRAND
from app.security import connection, seal

pytest_plugins = ["test_commerce"]


def test_fixture_rejects_secret_file_override_without_reading_it(monkeypatch):
    monkeypatch.setenv("MIGRATION_DATABASE_URL_FILE", "must-not-be-opened")
    with pytest.raises(RuntimeError, match="secret-file overrides"):
        require_fixture_environment()


def expire(order):
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "UPDATE orders SET reserved_until=now()-interval '1 minute' WHERE id=%s", (order["id"],)
        )
    run(jobs.maintenance())


def test_second_capture_refunds_only_extra_payment_and_preserves_fulfillment(staff):
    variant, order, headers, _ = approved(staff)
    first = start_payment(staff, order, headers)
    expire(order)
    second = start_payment(staff, order, headers)
    capture(second)
    capture(first)
    current = staff.get("/v1/order", headers=headers).json()
    assert current["status"] == "paid"
    with psycopg.connect(OWNER) as conn:
        assert conn.execute(
            "SELECT stock,reserved FROM variants WHERE id=%s", (variant,)
        ).fetchone() == (2, 0)
        refund = conn.execute(
            "SELECT r.id,r.amount,p.provider_payment FROM refunds r "
            "JOIN payments p ON r.payment_id=p.id"
        ).fetchone()
    assert refund[2] == first["id"]

    async def complete():
        async with connection() as conn:
            await commerce.refund_event(
                conn,
                {
                    "id": "rf_extra",
                    "receipt": str(refund[0]),
                    "payment_id": first["id"],
                    "amount": refund[1],
                    "status": "processed",
                },
            )

    run(complete())
    assert staff.get("/v1/order", headers=headers).json()["status"] == "paid"


def test_obsolete_quote_capture_preserves_new_reservation(staff):
    variant, order, headers, _ = approved(staff)
    old = start_payment(staff, order, headers)
    expire(order)
    newer = staff.post(
        f"/v1/admin/orders/{order['id']}/approve", json={"delivery_paise": 2000}
    ).json()
    fresh = start_payment(staff, newer, headers)
    capture(old)
    assert staff.get("/v1/order", headers=headers).json()["status"] == "payment_pending"
    with psycopg.connect(OWNER) as conn:
        assert (
            conn.execute("SELECT reserved FROM variants WHERE id=%s", (variant,)).fetchone()[0] == 1
        )
    capture(fresh)
    assert staff.get("/v1/order", headers=headers).json()["total_paise"] == newer["total_paise"]


def test_early_delivery_receipt_survives_worker_completion(staff, monkeypatch):
    identifier = uuid.uuid4()
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "INSERT INTO outbox(id,brand_id,kind,event_key,payload) VALUES(%s,%s,'whatsapp',%s,%s)",
            (identifier, BRAND, str(identifier), seal({"fixture": True})),
        )

    async def early(job):
        async with connection() as conn:
            await conn.execute(
                "INSERT INTO message_receipts(id,brand_id,status) "
                "VALUES('early-message',%s,'delivered')",
                (BRAND,),
            )
        return "early-message"

    monkeypatch.setattr(jobs, "dispatch", early)
    run(jobs.run_once())
    with psycopg.connect(OWNER) as conn:
        assert (
            conn.execute("SELECT status FROM outbox WHERE id=%s", (identifier,)).fetchone()[0]
            == "delivered"
        )


def test_manual_retry_cannot_repeat_uncertain_payment_post(staff, monkeypatch):
    _, order, headers, _ = approved(staff)
    start_payment(staff, order, headers)
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE payments SET provider_order=NULL,post_started=true")
        conn.execute("UPDATE outbox SET status='failed',attempts=5 WHERE kind='create_payment'")
        job = conn.execute("SELECT id FROM outbox WHERE kind='create_payment'").fetchone()[0]
    assert staff.post(f"/v1/admin/messages/{job}/retry").status_code == 200
    calls = []

    async def provider(method, path, **kwargs):
        calls.append(method)
        return {"items": []}

    monkeypatch.setattr(jobs.providers, "razorpay", provider)
    run(jobs.run_once())
    assert calls == ["GET"]


def test_partial_refund_then_cancellation_returns_only_remaining_money(staff):
    _, order, headers, _ = approved(staff)
    capture(start_payment(staff, order, headers))
    assert (
        staff.post(
            f"/v1/admin/orders/{order['id']}/refund",
            json={"amount": 1000, "reason": "Fixture adjustment"},
        ).status_code
        == 200
    )
    assert staff.post("/v1/order/cancel", headers=headers).status_code == 200
    with psycopg.connect(OWNER) as conn:
        assert conn.execute("SELECT sum(amount) FROM refunds").fetchone()[0] == order["total_paise"]


@pytest.mark.parametrize("dispatched", [False, True])
def test_full_refund_preserves_physical_delivery_and_cancellation(staff, dispatched):
    variant, order, headers, _ = approved(staff)
    payment = start_payment(staff, order, headers)
    capture(payment)
    if dispatched:
        assert (
            staff.post(
                f"/v1/admin/orders/{order['id']}/status",
                json={"status": "dispatched", "note": "Fixture dispatch"},
            ).status_code
            == 200
        )
    assert (
        staff.post(
            f"/v1/admin/orders/{order['id']}/refund",
            json={"amount": order["total_paise"], "reason": "Fixture full adjustment"},
        ).status_code
        == 200
    )
    with psycopg.connect(OWNER) as conn:
        identifier = str(conn.execute("SELECT id FROM refunds").fetchone()[0])

    async def complete():
        async with connection() as conn:
            await commerce.refund_event(
                conn,
                {
                    "id": "rf_full",
                    "receipt": identifier,
                    "payment_id": payment["id"],
                    "amount": order["total_paise"],
                    "status": "processed",
                },
            )

    run(complete())
    assert staff.get("/v1/order", headers=headers).json()["status"] == (
        "dispatched" if dispatched else "paid"
    )
    if dispatched:
        assert (
            staff.post(
                f"/v1/admin/orders/{order['id']}/status",
                json={"status": "delivered", "note": "Fixture delivery"},
            ).status_code
            == 200
        )
    else:
        assert staff.post("/v1/order/cancel", headers=headers).json()["status"] == "refunded"
        assert staff.post("/v1/order/cancel", headers=headers).json()["status"] == "refunded"
    with psycopg.connect(OWNER) as conn:
        assert conn.execute("SELECT stock FROM variants WHERE id=%s", (variant,)).fetchone()[0] == (
            2 if dispatched else 3
        )
        assert conn.execute("SELECT count(*) FROM refunds").fetchone()[0] == 1


def test_csv_invalid_second_row_rolls_back_first(staff):
    approved(staff)
    exported = staff.get("/v1/admin/products.csv").text
    lines = exported.splitlines()
    response = staff.post(
        "/v1/admin/products.csv",
        content="\n".join([*lines, "invalid,row"]),
        headers={"content-type": "text/csv"},
    )
    assert response.status_code == 422
    assert len(staff.get("/v1/admin/variants").json()) == 1


def test_session_expiry_and_cross_brand_order_token(staff):
    _, _, headers, _ = approved(staff)
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE orders SET brand_id='other-brand'")
    assert staff.get("/v1/order", headers=headers).status_code == 404
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE sessions SET expires_at=now()-interval '1 second'")
    assert staff.get("/v1/admin/orders").status_code == 401


def test_csv_roundtrip_retains_formula_like_copy(staff):
    approved(staff)
    item = staff.get("/v1/admin/variants").json()[0]
    payload = {key: value for key, value in item.items() if key not in {"id", "stock", "reserved"}}
    for description in ("=SUM(1,2)", "'Approved copy", "\t=1+1"):
        payload["product"]["description"] = description
        assert staff.put(f"/v1/admin/variants/{item['id']}", json=payload).status_code == 200
        exported = staff.get("/v1/admin/products.csv").text
        assert (
            staff.post(
                "/v1/admin/products.csv", content=exported, headers={"content-type": "text/csv"}
            ).status_code
            == 200
        )
        assert (
            staff.get("/v1/admin/variants").json()[0]["product"]["description"]
            == description.strip()
        )
