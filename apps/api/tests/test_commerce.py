"""Real PostgreSQL/Redis tests for money, authorization and recovery boundaries."""

import asyncio
import hashlib
import hmac
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

import psycopg
import pyotp
import pytest
from conftest import OWNER, READER
from fastapi.testclient import TestClient
from redis import Redis

from app import commerce, jobs, providers
from app.admin_cli import provision
from app.main import app
from app.security import connection

ORIGIN = "http://127.0.0.1:3000"
APP_DB = "postgresql://pakodi_app:local-app-only@127.0.0.1:54339/pakodi_mvp_test"
CUSTOMER = {
    "name": "Fixture Buyer",
    "phone": "+919876543210",
    "address": "10 Synthetic Test Road",
    "city": "Test City",
    "state_code": "36",
    "pincode": "500001",
}
PRODUCT = {
    "slug": "fixture-mix",
    "name": "Fixture Mix",
    "description": "Synthetic test product",
    "price_paise": 11800,
    "dietary": "non-veg",
    "ingredients": "Fixture ingredients",
    "allergens": "Fixture allergens",
    "nutrition": "Fixture nutrition",
    "net_quantity": "100 g",
    "shelf_life": "30 days",
    "manufacturer": "Fixture manufacturer",
    "consumer_care": "Fixture contact",
}
BUSINESS = {
    "legal_name": "Synthetic Test Seller",
    "address": "10 Synthetic Seller Street",
    "gstin": "36ABCDE1234F1Z5",
    "state_code": "36",
    "invoice_prefix": "PP",
    "delivery_gst_bps": 1800,
    "franchise_recipients": [],
    "staff_whatsapp_consent": False,
    "approved_for_sales": True,
}


def run(awaitable):
    with asyncio.Runner(loop_factory=asyncio.SelectorEventLoop) as runner:
        return runner.run(awaitable)


@pytest.fixture
def api(database, monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("COMMERCE_DATABASE_URL", APP_DB)
    monkeypatch.setenv("DATABASE_URL", READER)
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:63799/15")
    monkeypatch.setenv("PUBLIC_ORIGIN", ORIGIN)
    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_test_fixture")
    monkeypatch.setenv("RAZORPAY_WEBHOOK_SECRET", "synthetic-webhook-secret")
    # Only this fixture-owned database and Redis logical DB are cleared.
    with psycopg.connect(OWNER) as conn:
        conn.execute("""
TRUNCATE
admins,sessions,variants,orders,order_tokens,payments,refunds,provider_events,
outbox,enquiries,media,settings,invoice_counters,audit_events,settlements,message_receipts
RESTART IDENTITY CASCADE
""")
        conn.execute("DELETE FROM content_records WHERE kind='product' AND slug LIKE 'fixture-%'")
    Redis.from_url("redis://127.0.0.1:63799/15").flushdb()
    with TestClient(app, backend_options={"loop_factory": asyncio.SelectorEventLoop}) as client:
        client.headers["origin"] = ORIGIN
        yield client
    with psycopg.connect(OWNER) as conn:
        conn.execute("DELETE FROM content_records WHERE kind='product' AND slug LIKE 'fixture-%'")


@pytest.fixture
def staff(api):
    secret, recovery = run(provision("fixture-admin", "a-strong-fixture-password"))
    response = api.post(
        "/v1/admin/login",
        json={
            "username": "fixture-admin",
            "password": "a-strong-fixture-password",
            "code": pyotp.TOTP(secret).now(),
        },
    )
    assert response.status_code == 200, response.text
    api.headers["x-csrf-token"] = response.json()["csrf_token"]
    api.recovery_codes = recovery
    api.totp_secret = secret
    assert api.put("/v1/admin/settings", json=BUSINESS).status_code == 200
    return api


def add_product(staff, stock=3, suffix=""):
    product = {**PRODUCT, "slug": "fixture-mix" + suffix}
    response = staff.post(
        "/v1/admin/variants",
        json={
            "sku": "FIXTURE" + suffix,
            "product": product,
            "gst_bps": 1800,
            "hsn": "2106",
            "published": True,
        },
    )
    assert response.status_code == 201, response.text
    identifier = response.json()["id"]
    assert (
        staff.post(
            f"/v1/admin/variants/{identifier}/stock",
            json={"delta": stock, "reason": "Initial fixture stock"},
        ).status_code
        == 200
    )
    return identifier


def request_order(api, variant, consent=False, key=None):
    payload = {
        "request_key": key or str(uuid.uuid4()),
        "customer": CUSTOMER,
        "lines": [{"variant_id": variant, "quantity": 1}],
        "whatsapp_consent": consent,
    }
    response = api.post("/v1/orders", json=payload)
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    view = api.get("/v1/order", headers={"Authorization": "Bearer " + token}).json()
    return view, {"Authorization": "Bearer " + token}, payload


def approved(staff, stock=3, consent=False):
    variant = add_product(staff, stock)
    order, headers, payload = request_order(staff, variant, consent)
    response = staff.post(f"/v1/admin/orders/{order['id']}/approve", json={"delivery_paise": 1180})
    assert response.status_code == 200, response.text
    return variant, response.json(), headers, payload


def start_payment(api, order, headers):
    response = api.post(
        "/v1/order/payment", headers=headers, json={"quote_version": order["quote_version"]}
    )
    assert response.status_code == 200, response.text
    with psycopg.connect(OWNER) as conn:
        identifier = conn.execute(
            "SELECT id FROM payments WHERE order_id=%s ORDER BY created_at DESC LIMIT 1",
            (order["id"],),
        ).fetchone()[0]
        conn.execute(
            "UPDATE payments SET provider_order=%s WHERE id=%s",
            ("order_" + identifier.hex, identifier),
        )
    return {
        "id": "pay_" + identifier.hex,
        "order_id": "order_" + identifier.hex,
        "amount": order["total_paise"],
        "currency": "INR",
        "status": "captured",
    }


def capture(entity):
    async def operation():
        async with connection() as conn:
            await commerce.captured(conn, entity)

    run(operation())


def test_request_has_no_payment_and_private_lookup_is_scoped(staff):
    variant = add_product(staff)
    order, headers, payload = request_order(staff, variant)
    assert order["status"] == "requested"
    assert staff.get("/v1/order").status_code == 404
    assert staff.get("/v1/order", headers={"Authorization": "Bearer invalid"}).status_code == 404
    response = staff.post(
        "/v1/tracking", json={"reference": order["reference"], "phone": CUSTOMER["phone"]}
    )
    assert set(response.json()) == {"reference", "status", "updated_at"}
    assert (
        staff.post("/v1/order/payment", headers=headers, json={"quote_version": 1}).status_code
        == 409
    )
    assert staff.get("/v1/order/invoice", headers=headers).status_code == 409
    retry = staff.post("/v1/orders", json=payload)
    assert retry.json()["reference"] == order["reference"]


def test_approval_tax_and_changed_address_invalidate_quote(staff):
    _, order, headers, payload = approved(staff)
    assert order["total_paise"] == 12980
    assert order["tax"] == {"taxable": 11000, "cgst": 990, "sgst": 990, "igst": 0}
    payload["customer"] = {**CUSTOMER, "state_code": "29"}
    assert staff.put("/v1/order", headers=headers, json=payload).json()["status"] == "requested"
    assert (
        staff.post("/v1/order/payment", headers=headers, json={"quote_version": 1}).status_code
        == 409
    )
    result = staff.post(f"/v1/admin/orders/{order['id']}/approve", json={"delivery_paise": 1180})
    assert result.json()["tax"]["igst"] == 1980


def test_capture_is_idempotent_and_cancellation_restores_stock_once(staff):
    variant, order, headers, _ = approved(staff)
    entity = start_payment(staff, order, headers)
    capture(entity)
    capture(entity)
    paid = staff.get("/v1/order", headers=headers).json()
    assert paid["status"] == "paid" and paid["invoice_number"]
    pdf = staff.get("/v1/order/invoice", headers=headers)
    assert pdf.content.startswith(b"%PDF")
    assert staff.post("/v1/order/cancel", headers=headers).json()["status"] == "refund_pending"
    assert staff.post("/v1/order/cancel", headers=headers).json()["status"] == "refund_pending"
    with psycopg.connect(OWNER) as conn:
        assert conn.execute(
            "SELECT stock,reserved FROM variants WHERE id=%s", (variant,)
        ).fetchone() == (3, 0)
        assert conn.execute("SELECT count(*) FROM refunds").fetchone()[0] == 1


def test_dispatch_prevents_customer_cancellation(staff):
    _, order, headers, _ = approved(staff)
    capture(start_payment(staff, order, headers))
    assert (
        staff.post(
            f"/v1/admin/orders/{order['id']}/status", json={"status": "dispatched"}
        ).status_code
        == 200
    )
    assert staff.post("/v1/order/cancel", headers=headers).status_code == 409
    assert (
        staff.post(
            f"/v1/admin/orders/{order['id']}/status", json={"status": "delivered"}
        ).status_code
        == 200
    )


def test_last_item_concurrency_never_oversells(staff):
    variant = add_product(staff, stock=1)
    first, first_headers, _ = request_order(staff, variant)
    second, second_headers, _ = request_order(staff, variant)
    for order in (first, second):
        assert (
            staff.post(
                f"/v1/admin/orders/{order['id']}/approve", json={"delivery_paise": 0}
            ).status_code
            == 200
        )

    def attempt(headers):
        with TestClient(app, backend_options={"loop_factory": asyncio.SelectorEventLoop}) as client:
            return client.post(
                "/v1/order/payment",
                headers={**headers, "Origin": ORIGIN},
                json={"quote_version": 1},
            ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(attempt, [first_headers, second_headers])) == [200, 409]
    with psycopg.connect(OWNER) as conn:
        assert conn.execute(
            "SELECT stock,reserved FROM variants WHERE id=%s", (variant,)
        ).fetchone() == (1, 1)


def test_late_capture_without_stock_refunds(staff):
    variant, order, headers, _ = approved(staff, stock=1)
    entity = start_payment(staff, order, headers)
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "UPDATE orders SET reserved_until=now()-interval '1 minute' WHERE id=%s", (order["id"],)
        )
    run(jobs.maintenance())
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE variants SET stock=0 WHERE id=%s", (variant,))
    capture(entity)
    assert staff.get("/v1/order", headers=headers).json()["status"] == "refund_pending"


def test_cancelled_payment_capture_never_fulfills(staff):
    _, order, headers, _ = approved(staff)
    entity = start_payment(staff, order, headers)
    assert staff.post("/v1/order/cancel", headers=headers).status_code == 200
    capture(entity)
    assert staff.get("/v1/order", headers=headers).json()["status"] == "refund_pending"


def test_quote_expiry_and_amount_mismatch(staff):
    _, order, headers, _ = approved(staff)
    entity = start_payment(staff, order, headers)
    with pytest.raises(ValueError):
        capture({**entity, "amount": 1})
    with psycopg.connect(OWNER) as conn:
        conn.execute("""
UPDATE orders SET quote_expires_at=now()-interval '1
minute',reserved_until=now()-interval '1 minute'
""")
    run(jobs.maintenance())
    assert (
        staff.post("/v1/order/payment", headers=headers, json={"quote_version": 1}).status_code
        == 409
    )


def test_raw_webhook_signature_and_duplicate_event(staff):
    _, order, headers, _ = approved(staff)
    entity = start_payment(staff, order, headers)
    raw = json.dumps(
        {"event": "payment.captured", "payload": {"payment": {"entity": entity}}}
    ).encode()
    signature = hmac.new(b"synthetic-webhook-secret", raw, hashlib.sha256).hexdigest()
    assert staff.post("/v1/webhooks/razorpay", content=raw).status_code == 400
    for _ in range(2):
        assert (
            staff.post(
                "/v1/webhooks/razorpay",
                content=raw,
                headers={"x-razorpay-signature": signature, "x-razorpay-event-id": "fixture-event"},
            ).status_code
            == 200
        )
    with psycopg.connect(OWNER) as conn:
        assert conn.execute("SELECT count(*) FROM provider_events").fetchone()[0] == 1
        conn.execute("UPDATE outbox SET status='sent' WHERE kind='create_payment'")
    run(jobs.run_once())
    assert staff.get("/v1/order", headers=headers).json()["status"] == "paid"


def test_refund_processed_before_pending_does_not_reverse(staff):
    _, order, headers, _ = approved(staff)
    entity = start_payment(staff, order, headers)
    capture(entity)
    staff.post("/v1/order/cancel", headers=headers)
    with psycopg.connect(OWNER) as conn:
        identifier = str(conn.execute("SELECT id FROM refunds").fetchone()[0])

    async def events():
        async with connection() as conn:
            event = {
                "id": "rfnd_fixture",
                "payment_id": entity["id"],
                "receipt": identifier,
                "amount": order["total_paise"],
                "status": "processed",
            }
            await commerce.refund_event(conn, event)
            await commerce.refund_event(conn, {**event, "status": "pending"})

    run(events())
    assert staff.get("/v1/order", headers=headers).json()["status"] == "refunded"


def test_admin_csrf_totp_replay_and_recovery_code(staff):
    response = staff.put("/v1/admin/settings", headers={"x-csrf-token": "wrong"}, json=BUSINESS)
    assert response.status_code == 403
    assert (
        staff.put(
            "/v1/admin/settings", headers={"origin": "https://attacker.invalid"}, json=BUSINESS
        ).status_code
        == 403
    )
    payload = {
        "username": "fixture-admin",
        "password": "a-strong-fixture-password",
        "code": pyotp.TOTP(staff.totp_secret).now(),
    }
    assert staff.post("/v1/admin/login", json=payload).status_code == 401
    payload["code"] = staff.recovery_codes[0]
    assert staff.post("/v1/admin/login", json=payload).status_code == 200
    assert staff.post("/v1/admin/login", json=payload).status_code == 401


@pytest.mark.parametrize(
    "path", ["orders", "variants", "content", "settings", "messages", "media", "enquiries"]
)
def test_anonymous_admin_denied(api, path):
    assert api.get("/v1/admin/" + path).status_code == 401


def test_app_rls_and_audit_immutability(api):
    with psycopg.connect(APP_DB) as conn:
        assert conn.execute("SELECT count(*) FROM orders").fetchone()[0] == 0
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            conn.execute("INSERT INTO settings(brand_id,data) VALUES('other','{}')")
    with psycopg.connect(APP_DB) as conn:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            conn.execute("DELETE FROM audit_events")


def test_link_rotation_and_opt_out(staff, monkeypatch):
    _, order, headers, _ = approved(staff, consent=True)
    assert staff.post("/v1/order/opt-out", headers=headers).status_code == 200

    async def should_not_send(_payload):
        raise AssertionError("Opted-out customer must not be messaged")

    monkeypatch.setattr(providers, "send_whatsapp", should_not_send)
    run(jobs.run_once())
    with psycopg.connect(OWNER) as conn:
        assert (
            conn.execute("SELECT status FROM outbox WHERE kind='whatsapp'").fetchone()[0]
            == "suppressed"
        )
    recovered = staff.post(f"/v1/admin/orders/{order['id']}/recover-link")
    assert recovered.status_code == 200
    assert staff.get("/v1/order", headers=headers).status_code == 404
    assert (
        staff.get(
            "/v1/order", headers={"Authorization": "Bearer " + recovered.json()["access_token"]}
        ).status_code
        == 200
    )


def test_media_rejects_svg_and_oversized_body(staff):
    assert (
        staff.post("/v1/admin/media?alt=Fixture", content=b'<svg onload="alert(1)"/>').status_code
        == 422
    )
    assert staff.post("/v1/admin/media?alt=Fixture", content=b"x" * 5_000_001).status_code == 413


def test_enquiry_is_saved_without_messaging_provider(api):
    payload = {
        "name": "Fixture Lead",
        "phone": "+919876543211",
        "email": "fixture@example.invalid",
        "city": "Test City",
        "preferred_model": "Cart",
        "budget": "To discuss",
        "source": "test",
        "campaign": "fixture",
    }
    assert api.post("/v1/enquiries", json=payload).status_code == 201
    with psycopg.connect(OWNER) as conn:
        assert (
            conn.execute("SELECT attribution->>'campaign' FROM enquiries").fetchone()[0]
            == "fixture"
        )


def test_stock_adjustment_cannot_consume_reservation(staff):
    variant, order, headers, _ = approved(staff, stock=1)
    start_payment(staff, order, headers)
    assert (
        staff.post(
            f"/v1/admin/variants/{variant}/stock",
            json={"delta": -1, "reason": "Fixture correction"},
        ).status_code
        == 409
    )


def test_worker_failure_is_durable(staff, monkeypatch):
    approved(staff, consent=True)

    async def outage(_payload):
        raise RuntimeError("private-provider-payload-must-not-leak")

    monkeypatch.setattr(providers, "send_whatsapp", outage)
    run(jobs.run_once())
    result = staff.get("/v1/admin/messages").json()
    assert result[0]["status"] == "pending"
    assert result[0]["last_error"] == "RuntimeError"
    assert "private-provider" not in json.dumps(result)
