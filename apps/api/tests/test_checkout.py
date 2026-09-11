"""Immediate checkout uses real isolated PostgreSQL and the existing payment machinery."""

import uuid
from datetime import UTC, datetime

import psycopg
from conftest import OWNER
from psycopg.types.json import Jsonb
from test_commerce import CUSTOMER, PRODUCT, add_product, run
from test_commerce import api as api_fixture
from test_commerce import staff as staff_fixture

from app import checkout
from app.security import connection, seal, unseal

api = api_fixture
staff = staff_fixture


def setup_delivery(staff, *, fresh=False):
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            """INSERT INTO content_records(brand_id,kind,slug,published,payload)
        VALUES('patnam-pakodi','outlet','fixture-pilot',true,%s)
        ON CONFLICT(brand_id,kind,slug) DO UPDATE SET payload=excluded.payload,published=true""",
            (
                Jsonb(
                    {
                        "slug": "fixture-pilot",
                        "name": "Fixture pilot outlet",
                        "city": "Test City",
                        "pincode": "500001",
                    }
                ),
            ),
        )
    config = {
        "packaged_enabled": True,
        "fresh_enabled": fresh,
        "outlet_slug": "fixture-pilot",
        "preparation_minutes": 20,
        "hours": [{"day": day, "opens": "00:00", "closes": "24:00"} for day in range(7)],
        "rules": [
            {"mode": mode, "pincode": "500001", "state_code": "36", "fee_paise": 4000}
            for mode in ("fresh", "packaged")
        ],
    }
    result = staff.put("/v1/admin/fulfilment", json=config)
    assert result.status_code == 200, result.text
    return config


def fresh_product(staff):
    result = staff.post(
        "/v1/admin/variants",
        json={
            "sku": "FIXTURE-FRESH",
            "product": {
                **PRODUCT,
                "slug": "fixture-fresh",
                "mode": "fresh",
                "outlet_slug": "fixture-pilot",
                "shelf_life": "",
                "manufacturer": "",
            },
            "gst_bps": 1800,
            "hsn": "2106",
            "published": True,
        },
    )
    assert result.status_code == 201, result.text
    identifier = result.json()["id"]
    assert (
        staff.post(
            f"/v1/admin/variants/{identifier}/stock",
            json={"delta": 5, "reason": "Fixture portions"},
        ).status_code
        == 200
    )
    return identifier


def reviewed(staff, identifier, mode="packaged"):
    payload = {
        "mode": mode,
        "customer": CUSTOMER,
        "lines": [{"variant_id": identifier, "quantity": 1}],
    }
    quote = staff.post("/v1/checkout/quote", json=payload)
    assert quote.status_code == 200, quote.text
    assert quote.json()["total_paise"] == 15800
    payload.update(
        request_key=str(uuid.uuid4()),
        quote_token=quote.json()["quote_token"],
        whatsapp_consent=False,
    )
    return payload


def test_instant_checkout_server_total_retry_and_legacy_protection(staff):
    setup_delivery(staff)
    variant = add_product(staff)
    payload = reviewed(staff, variant)
    receipt = staff.post("/v1/checkout/orders", json=payload)
    assert receipt.status_code == 201, receipt.text
    headers = {"Authorization": "Bearer " + receipt.json()["access_token"]}
    order = staff.get("/v1/order", headers=headers).json()
    assert order["status"] == "approved"
    assert order["checkout_kind"] == "instant"
    assert order["total_paise"] == 15800
    retry = staff.post("/v1/checkout/orders", json=payload)
    assert retry.json()["reference"] == receipt.json()["reference"]
    assert (
        staff.post(
            f"/v1/admin/orders/{order['id']}/approve", json={"delivery_paise": 0}
        ).status_code
        == 409
    )
    assert (
        staff.put(
            "/v1/order",
            headers=headers,
            json={
                key: payload[key]
                for key in ("request_key", "customer", "lines", "whatsapp_consent")
            },
        ).status_code
        == 409
    )
    payment = staff.post(
        "/v1/order/payment", headers=headers, json={"quote_version": order["quote_version"]}
    )
    assert payment.status_code == 200, payment.text
    assert payment.json()["amount"] == 15800


def test_checkout_rejects_tampered_expired_changed_fee_and_address(staff):
    config = setup_delivery(staff)
    variant = add_product(staff)
    payload = reviewed(staff, variant)
    bad = {**payload, "quote_token": "x" * 80}
    assert staff.post("/v1/checkout/orders", json=bad).status_code == 409
    expired = unseal(payload["quote_token"])
    expired["expires"] = 0
    assert (
        staff.post(
            "/v1/checkout/orders", json={**payload, "quote_token": seal(expired)}
        ).status_code
        == 409
    )
    changed = {**payload, "customer": {**CUSTOMER, "pincode": "500002"}}
    assert staff.post("/v1/checkout/orders", json=changed).status_code == 409
    config["rules"][1]["fee_paise"] = 5000
    assert staff.put("/v1/admin/fulfilment", json=config).status_code == 200
    assert staff.post("/v1/checkout/orders", json=payload).status_code == 409
    with psycopg.connect(OWNER) as conn:
        assert conn.execute("SELECT count(*) FROM orders").fetchone()[0] == 0


def test_fresh_mode_availability_and_preparation_cancellation_boundary(staff):
    config = setup_delivery(staff, fresh=True)
    variant = fresh_product(staff)
    assert staff.get("/v1/catalog?mode=packaged").json() == []
    assert len(staff.get("/v1/catalog?mode=fresh").json()) == 1
    payload = reviewed(staff, variant, "fresh")
    assert (
        staff.post(
            "/v1/orders",
            json={
                key: payload[key]
                for key in ("request_key", "customer", "lines", "whatsapp_consent")
            },
        ).status_code
        == 409
    )
    receipt = staff.post("/v1/checkout/orders", json=payload)
    assert receipt.status_code == 201, receipt.text
    headers = {"Authorization": "Bearer " + receipt.json()["access_token"]}
    order = staff.get("/v1/order", headers=headers).json()
    assert order["fulfilment"]["outlet_slug"] == "fixture-pilot"
    # Exercise the post-payment transition without invoking a real provider.
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE orders SET status='paid' WHERE id=%s", (order["id"],))
    assert (
        staff.post(
            f"/v1/admin/orders/{order['id']}/status", json={"status": "dispatched"}
        ).status_code
        == 409
    )
    assert (
        staff.post(
            f"/v1/admin/orders/{order['id']}/status", json={"status": "preparing"}
        ).status_code
        == 200
    )
    assert staff.post("/v1/order/cancel", headers=headers).status_code == 409
    assert (
        staff.post(
            f"/v1/admin/orders/{order['id']}/status", json={"status": "dispatched"}
        ).status_code
        == 200
    )
    config["fresh_paused"] = True
    assert staff.put("/v1/admin/fulfilment", json=config).status_code == 200
    assert not staff.get("/v1/serviceability?mode=fresh&pincode=500001").json()["available"]
    assert (
        staff.post(
            "/v1/checkout/quote", json={key: payload[key] for key in ("mode", "customer", "lines")}
        ).status_code
        == 409
    )


def test_fulfilment_requires_auth_and_valid_configuration(api, staff):
    config = setup_delivery(staff, fresh=True)
    duplicated = {**config, "rules": config["rules"] * 2}
    assert staff.put("/v1/admin/fulfilment", json=duplicated).status_code == 422
    assert (
        staff.put("/v1/admin/fulfilment", json={**config, "outlet_slug": "missing"}).status_code
        == 422
    )
    assert not staff.get("/v1/serviceability?mode=packaged&pincode=999999").json()["available"]
    api.cookies.clear()
    assert api.get("/v1/admin/fulfilment").status_code == 401
    assert api.put("/v1/admin/fulfilment", json=config).status_code == 401


def test_closed_hours_and_payment_revalidation(staff):
    config = setup_delivery(staff, fresh=True)
    variant = add_product(staff)
    payload = reviewed(staff, variant)
    receipt = staff.post("/v1/checkout/orders", json=payload).json()
    headers = {"Authorization": "Bearer " + receipt["access_token"]}
    order = staff.get("/v1/order", headers=headers).json()
    config["packaged_enabled"] = False
    config["hours"] = [{"day": 0, "opens": "09:00", "closes": "10:00"}]
    assert staff.put("/v1/admin/fulfilment", json=config).status_code == 200
    assert (
        staff.post(
            "/v1/order/payment", headers=headers, json={"quote_version": order["quote_version"]}
        ).status_code
        == 409
    )

    async def closed():
        async with connection() as conn:
            return await checkout.availability(
                conn, "fresh", "500001", now=datetime(2026, 9, 14, 5, 0, tzinfo=UTC)
            )

    assert not run(closed()).available  # Monday 10:30 IST, after closing.


def test_concurrent_payment_reserves_last_fresh_portion_and_serializes_cancellation(staff):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from test_commerce import capture, start_payment

    setup_delivery(staff, fresh=True)
    variant = fresh_product(staff)
    staff.post(
        f"/v1/admin/variants/{variant}/stock",
        json={"delta": -4, "reason": "One final fixture portion"},
    )
    receipts = [
        staff.post("/v1/checkout/orders", json=reviewed(staff, variant, "fresh")).json()
        for _ in range(2)
    ]
    headers = [{"Authorization": "Bearer " + receipt["access_token"]} for receipt in receipts]
    orders = [staff.get("/v1/order", headers=auth).json() for auth in headers]
    barrier = Barrier(2)

    def pay(index):
        barrier.wait(timeout=10)
        return staff.post(
            "/v1/order/payment",
            headers=headers[index],
            json={"quote_version": orders[index]["quote_version"]},
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(pay, range(2)))
    assert sorted(result.status_code for result in results) == [200, 409]
    winner = next(index for index, result in enumerate(results) if result.status_code == 200)
    order, auth = orders[winner], headers[winner]
    capture(start_payment(staff, order, auth))
    barrier = Barrier(2)

    def change(action):
        barrier.wait(timeout=10)
        return (
            staff.post("/v1/order/cancel", headers=auth)
            if action == "cancel"
            else staff.post(f"/v1/admin/orders/{order['id']}/status", json={"status": "preparing"})
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(change, ("cancel", "prepare")))
    assert sorted(result.status_code for result in outcomes) == [200, 409]
    final = staff.get("/v1/order", headers=auth).json()
    with psycopg.connect(OWNER) as conn:
        stock = conn.execute(
            "SELECT stock,reserved FROM variants WHERE id=%s", (variant,)
        ).fetchone()
        refunds = conn.execute(
            "SELECT count(*) FROM refunds WHERE order_id=%s", (order["id"],)
        ).fetchone()[0]
    if final["status"] == "preparing":
        assert stock == (0, 0)
        assert refunds == 0
    else:
        assert final["status"] == "refund_pending"
        assert stock == (1, 0)
        assert refunds == 1


def test_instant_retry_and_paid_fresh_cancel_are_idempotent(staff):
    from concurrent.futures import ThreadPoolExecutor

    from test_commerce import capture, start_payment

    setup_delivery(staff, fresh=True)
    variant = fresh_product(staff)
    payload = reviewed(staff, variant, "fresh")
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(lambda _: staff.post("/v1/checkout/orders", json=payload), range(2))
        )
    assert all(response.status_code == 201 for response in responses)
    assert responses[0].json()["reference"] == responses[1].json()["reference"]
    # Retried receipts may issue separate private links to the same single order.
    assert all(
        staff.get(
            "/v1/order", headers={"Authorization": "Bearer " + response.json()["access_token"]}
        ).status_code
        == 200
        for response in responses
    )
    auth = {"Authorization": "Bearer " + responses[0].json()["access_token"]}
    order = staff.get("/v1/order", headers=auth).json()
    entity = start_payment(staff, order, auth)
    capture(entity)
    capture(entity)
    for _ in range(2):
        assert staff.post("/v1/order/cancel", headers=auth).status_code == 200
    with psycopg.connect(OWNER) as conn:
        assert conn.execute(
            "SELECT stock,reserved FROM variants WHERE id=%s", (variant,)
        ).fetchone() == (5, 0)
        assert conn.execute("SELECT count(*) FROM refunds").fetchone()[0] == 1
        assert conn.execute("SELECT count(*) FROM orders").fetchone()[0] == 1
        assert (
            conn.execute("SELECT count(*) FROM orders WHERE invoice_number IS NOT NULL").fetchone()[
                0
            ]
            == 1
        )


def test_staff_preparation_cancellation_refunds_remaining_balance_without_restock(staff):
    from concurrent.futures import ThreadPoolExecutor

    from test_commerce import capture, start_payment

    setup_delivery(staff, fresh=True)
    variant = fresh_product(staff)
    receipt = staff.post("/v1/checkout/orders", json=reviewed(staff, variant, "fresh"))
    assert receipt.status_code == 201
    auth = {"Authorization": "Bearer " + receipt.json()["access_token"]}
    order = staff.get("/v1/order", headers=auth).json()
    capture(start_payment(staff, order, auth))
    path = f"/v1/admin/orders/{order['id']}"
    assert staff.post(path + "/status", json={"status": "preparing"}).status_code == 200
    assert (
        staff.post("/v1/order/cancel", headers=auth, json={"allow_preparing": True}).status_code
        == 409
    )
    assert staff.post(path + "/cancel", headers={"X-CSRF-Token": "invalid"}).status_code == 403
    assert (
        staff.post(
            path + "/refund", json={"amount": 1000, "reason": "Synthetic partial adjustment"}
        ).status_code
        == 200
    )
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: staff.post(path + "/cancel"), range(2)))
    assert all(response.status_code == 200 for response in responses)
    assert all(response.json()["status"] == "refund_pending" for response in responses)
    assert staff.post(path + "/status", json={"status": "dispatched"}).status_code == 409
    with psycopg.connect(OWNER) as conn:
        assert conn.execute(
            "SELECT stock,reserved FROM variants WHERE id=%s", (variant,)
        ).fetchone() == (4, 0)
        assert conn.execute("SELECT count(*),sum(amount) FROM refunds").fetchone() == (2, 15800)
        assert (
            conn.execute(
                "SELECT count(*) FROM audit_events WHERE action='order.cancelled'"
            ).fetchone()[0]
            == 1
        )


def test_fulfilment_settings_are_isolated_by_rls(staff):
    import pytest
    from test_commerce import APP_DB

    setup_delivery(staff)
    with psycopg.connect(APP_DB) as conn:
        assert conn.execute("SELECT count(*) FROM fulfilment_settings").fetchone()[0] == 0
        conn.execute("SELECT set_config('app.brand_id','other',true)")
        assert conn.execute("SELECT count(*) FROM fulfilment_settings").fetchone()[0] == 0
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            conn.execute(
                "INSERT INTO fulfilment_settings(brand_id,data) VALUES('patnam-pakodi','{}')"
            )
