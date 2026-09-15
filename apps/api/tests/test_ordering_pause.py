"""A launch pause blocks purchases without stranding existing financial work."""

import json
import uuid

import psycopg
import pytest
from conftest import OWNER
from test_checkout import fresh_product, reviewed, setup_delivery
from test_commerce import CUSTOMER, add_product, approved, capture, start_payment

from app.config import ordering_enabled
from app.seed import SOURCE, apply_records

pytest_plugins = ["test_commerce"]


def test_ordering_defaults_closed_and_only_explicit_true_enables_it(monkeypatch, client):
    monkeypatch.delenv("ORDERING_ENABLED", raising=False)
    assert not ordering_enabled()
    assert client.get("/v1/storefront").json()["ordering_enabled"] is False
    for value in ("false", "", "1", "yes", "tru"):
        monkeypatch.setenv("ORDERING_ENABLED", value)
        assert not ordering_enabled()
    monkeypatch.setenv("ORDERING_ENABLED", "true")
    assert client.get("/v1/storefront").json()["ordering_enabled"] is True


@pytest.mark.parametrize("mode", ["fresh", "packaged"])
def test_pause_blocks_review_creation_retries_and_serviceability(staff, monkeypatch, mode):
    setup_delivery(staff, fresh=True)
    variant = fresh_product(staff) if mode == "fresh" else add_product(staff)
    payload = reviewed(staff, variant, mode)
    monkeypatch.setenv("ORDERING_ENABLED", "false")
    quote = {key: payload[key] for key in ("mode", "customer", "lines")}
    legacy = {key: payload[key] for key in ("request_key", "customer", "lines", "whatsapp_consent")}
    for path, body in (
        ("/v1/checkout/quote", quote),
        ("/v1/checkout/orders", payload),
        ("/v1/orders", legacy),
    ):
        response = staff.post(path, json=body)
        assert response.status_code == 409, response.text
        assert "paused" in response.json()["detail"]
    assert staff.get(f"/v1/serviceability?mode={mode}&pincode=500001").json()["available"] is False
    with psycopg.connect(OWNER) as conn:
        for table in ("orders", "payments", "outbox"):
            assert conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0
        assert (
            conn.execute("SELECT reserved FROM variants WHERE id=%s", (variant,)).fetchone()[0] == 0
        )


def test_pause_blocks_old_quotes_edits_and_idempotent_replays(staff, monkeypatch):
    _, order, headers, payload = approved(staff)
    monkeypatch.setenv("ORDERING_ENABLED", "false")
    for method, path, body in (
        (staff.post, "/v1/orders", payload),
        (staff.put, "/v1/order", payload),
        (staff.post, "/v1/order/payment", {"quote_version": order["quote_version"]}),
    ):
        response = method(path, headers=headers, json=body)
        assert response.status_code == 409
        assert "paused" in response.json()["detail"]
    current = staff.get("/v1/order", headers=headers).json()
    assert current == order
    assert staff.get("/v1/admin/orders").status_code == 200
    assert staff.post("/v1/order/cancel", headers=headers).status_code == 200
    with psycopg.connect(OWNER) as conn:
        assert conn.execute("SELECT count(*) FROM payments").fetchone()[0] == 0
        assert conn.execute("SELECT count(*) FROM orders").fetchone()[0] == 1


def test_inflight_capture_invoice_refund_and_optout_survive_pause(staff, monkeypatch):
    variant, order, headers, _ = approved(staff)
    event = start_payment(staff, order, headers)
    monkeypatch.setenv("ORDERING_ENABLED", "false")
    capture(event)
    capture(event)
    current = staff.get("/v1/order", headers=headers).json()
    assert current["status"] == "paid" and current["invoice_number"]
    assert staff.get("/v1/order/invoice", headers=headers).status_code == 200
    assert staff.post("/v1/order/opt-out", headers=headers).status_code == 200
    assert staff.post("/v1/order/cancel", headers=headers).status_code == 200
    with psycopg.connect(OWNER) as conn:
        assert conn.execute("SELECT count(*) FROM refunds").fetchone()[0] == 1
        assert conn.execute(
            "SELECT stock,reserved FROM variants WHERE id=%s", (variant,)
        ).fetchone() == (3, 0)


def test_menu_launch_update_is_repeatable_and_preserves_other_records(staff):
    variant, order, _, _ = approved(staff)
    records = json.loads(SOURCE.read_text(encoding="utf-8"))
    with psycopg.connect(OWNER) as conn:
        before = conn.execute(
            "SELECT id,product,stock,reserved FROM variants WHERE id=%s", (variant,)
        ).fetchone()
        outlets = conn.execute(
            "SELECT slug,payload FROM content_records WHERE kind='outlet' ORDER BY slug"
        ).fetchall()
        # Mimic an old installed menu, while retaining its original editorial payload.
        conn.execute(
            "UPDATE content_records SET published=true "
            "WHERE kind='menu' AND slug='kaju-chicken-pakodi'"
        )
        for _ in range(2):
            assert apply_records(conn, records, menu_launch=True) == 14
        assert (
            conn.execute(
                "SELECT count(*) FROM content_records WHERE kind='menu' AND published"
            ).fetchone()[0]
            == 4
        )
        assert conn.execute(
            "SELECT payload->>'name',published FROM content_records "
            "WHERE kind='menu' AND slug='kaju-chicken-pakodi'"
        ).fetchone() == ("Kaju Chicken Pakodi", False)
        assert (
            conn.execute(
                "SELECT id,product,stock,reserved FROM variants WHERE id=%s", (variant,)
            ).fetchone()
            == before
        )
        assert (
            conn.execute(
                "SELECT slug,payload FROM content_records WHERE kind='outlet' ORDER BY slug"
            ).fetchall()
            == outlets
        )
        assert (
            conn.execute("SELECT status FROM orders WHERE id=%s", (order["id"],)).fetchone()[0]
            == "approved"
        )


def test_bundled_brochure_download_and_persisted_enquiry_work_while_paused(staff, monkeypatch):
    monkeypatch.setenv("ORDERING_ENABLED", "false")
    monkeypatch.delenv("BROCHURE_PATH", raising=False)
    receipt = staff.post(
        "/v1/enquiries/quick",
        json={"request_key": str(uuid.uuid4()), "phone": CUSTOMER["phone"], "purpose": "brochure"},
    )
    assert receipt.status_code == 201, receipt.text
    assert receipt.json()["brochure_url"] == "/api/v1/brochure"
    download = staff.get("/v1/brochure")
    assert download.status_code == 200
    assert download.headers["content-type"] == "application/pdf"
    assert download.content.startswith(b"%PDF-") and len(download.content) < 5_000_000
    with psycopg.connect(OWNER) as conn:
        assert conn.execute("SELECT count(*) FROM enquiries").fetchone()[0] == 1


def test_site_expansion_preserves_history_and_only_publishes_kukatpally(staff):
    variant, order, _, _ = approved(staff)
    records = json.loads(SOURCE.read_text(encoding="utf-8"))
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE content_records SET published=true WHERE kind='outlet'")
        outlets = conn.execute(
            "SELECT slug,payload FROM content_records WHERE kind='outlet' ORDER BY slug"
        ).fetchall()
        before = conn.execute(
            "SELECT id,product,stock,reserved FROM variants WHERE id=%s", (variant,)
        ).fetchone()
        for _ in range(2):
            assert apply_records(conn, records, site_expansion=True) == 16
        assert conn.execute(
            "SELECT slug FROM content_records WHERE kind='outlet' AND published"
        ).fetchall() == [("kukatpally",)]
        assert (
            conn.execute(
                "SELECT slug,payload FROM content_records WHERE kind='outlet' ORDER BY slug"
            ).fetchall()
            == outlets
        )
        assert (
            conn.execute(
                "SELECT id,product,stock,reserved FROM variants WHERE id=%s", (variant,)
            ).fetchone()
            == before
        )
        assert (
            conn.execute("SELECT status FROM orders WHERE id=%s", (order["id"],)).fetchone()[0]
            == "approved"
        )
        assert (
            conn.execute(
                "SELECT payload->>'heading' FROM content_records "
                "WHERE kind='page' AND slug='branches'"
            ).fetchone()[0]
            == "Your pakodi break starts in Kukatpally."
        )
