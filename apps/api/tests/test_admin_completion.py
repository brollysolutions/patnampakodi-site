"""Admin reporting and personal-data boundaries using disposable fixtures only."""

import csv
import io
import uuid

import psycopg
from conftest import OWNER
from psycopg.types.json import Jsonb
from test_commerce import approved, capture, run, start_payment

from app import jobs

pytest_plugins = ["test_commerce"]


def lead(staff, **changes):
    response = staff.post(
        "/v1/enquiries/quick",
        json={
            "request_key": str(uuid.uuid4()),
            "phone": "+919876543210",
            "purpose": "brochure",
            "source": "original",
            **changes,
        },
    )
    assert response.status_code == 201, response.text
    return staff.get("/v1/admin/enquiries").json()[0]


def test_enrichment_preserves_source_and_requires_csrf_and_brand(staff):
    item = lead(staff)
    payload = {
        "phone": item["details"]["phone"],
        "name": "Updated Fixture",
        "notes": "Discussed a cart",
    }
    response = staff.put("/v1/admin/enquiries/" + item["id"], json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["details"]["purpose"] == "brochure"
    assert response.json()["attribution"] == item["attribution"]
    again = staff.put("/v1/admin/enquiries/" + item["id"], json={"phone": item["details"]["phone"]})
    assert again.json()["details"]["name"] == "Updated Fixture"
    assert again.json()["details"]["notes"] == "Discussed a cart"
    assert (
        staff.put(
            "/v1/admin/enquiries/" + item["id"], json=payload, headers={"X-CSRF-Token": "invalid"}
        ).status_code
        == 403
    )
    assert (
        staff.put(
            "/v1/admin/enquiries/" + item["id"], json={**payload, "purpose": "contact"}
        ).status_code
        == 422
    )
    with psycopg.connect(OWNER) as conn:
        audit = conn.execute(
            "SELECT changes FROM audit_events WHERE action='enquiry.enriched' "
            "ORDER BY created_at LIMIT 1"
        ).fetchone()[0]
        assert audit == {"fields": ["name", "notes", "phone"]}
        conn.execute(
            "UPDATE enquiries SET brand_id='other-fixture-brand' WHERE id=%s", (item["id"],)
        )
    assert staff.put("/v1/admin/enquiries/" + item["id"], json=payload).status_code == 404


def test_enquiry_export_uses_inclusive_india_dates_and_literal_cells(staff):
    item = lead(staff)
    details = {**item["details"], "name": '\t=HYPERLINK("unsafe")', "notes": "+SUM(1,2)"}
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "UPDATE enquiries SET details=%s,created_at='2026-09-10 18:30:00+00' WHERE id=%s",
            (Jsonb(details), item["id"]),
        )
    response = staff.get("/v1/admin/enquiries.csv?start=2026-09-11&end=2026-09-11")
    assert response.status_code == 200, response.text
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert len(rows) == 1
    assert rows[0]["name"] == '\'\t=HYPERLINK("unsafe")'
    assert rows[0]["phone"].startswith("'+91")
    assert rows[0]["notes"] == "'+SUM(1,2)"
    assert (
        list(
            csv.DictReader(
                io.StringIO(
                    staff.get("/v1/admin/enquiries.csv?start=2026-09-10&end=2026-09-10").text
                )
            )
        )
        == []
    )
    assert (
        list(
            csv.DictReader(
                io.StringIO(
                    staff.get(
                        "/v1/admin/enquiries.csv?start=2026-09-11&end=2026-09-11&status=won"
                    ).text
                )
            )
        )
        == []
    )
    assert staff.get("/v1/admin/enquiries.csv?start=2026-09-12&end=2026-09-11").status_code == 422
    assert staff.get("/v1/admin/enquiries.csv?start=2024-01-01&end=2026-09-11").status_code == 422
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "UPDATE enquiries SET brand_id='other-fixture-brand' WHERE id=%s", (item["id"],)
        )
    assert (
        list(
            csv.DictReader(
                io.StringIO(
                    staff.get("/v1/admin/enquiries.csv?start=2026-09-11&end=2026-09-11").text
                )
            )
        )
        == []
    )


def test_reports_and_media_are_private(api):
    for path in [
        "/v1/admin/enquiries.csv?start=2026-09-11&end=2026-09-11",
        "/v1/admin/sales-summary?start=2026-09-11&end=2026-09-11",
        "/v1/admin/media/" + str(uuid.uuid4()),
    ]:
        assert api.get(path).status_code == 401


def test_enquiry_export_rejects_overflow_instead_of_silently_truncating(staff):
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "INSERT INTO enquiries(id,brand_id,details,attribution,created_at) "
            "SELECT gen_random_uuid(),'patnam-pakodi','{}','{}',"
            "'2026-09-11 12:00:00+00' FROM generate_series(1,10001)"
        )
    response = staff.get("/v1/admin/enquiries.csv?start=2026-09-11&end=2026-09-11")
    assert response.status_code == 422
    assert "shorter period" in response.json()["detail"]


def test_extra_capture_refunds_do_not_reduce_sales_or_duplicate_invoices(staff):
    _, order, headers, _ = approved(staff)
    first = start_payment(staff, order, headers)
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "UPDATE orders SET reserved_until=now()-interval '1 minute' WHERE id=%s", (order["id"],)
        )
    run(jobs.maintenance())
    second = start_payment(staff, order, headers)
    capture(second)
    capture(first)
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE refunds SET status='processed' WHERE order_id=%s", (order["id"],))
        conn.execute(
            "UPDATE orders SET invoiced_at='2026-09-11 12:00:00+00' WHERE id=%s", (order["id"],)
        )
    result = staff.get("/v1/admin/sales-summary?start=2026-09-11&end=2026-09-11").json()
    assert result["orders"] == 1
    assert result["gross_paise"] == order["total_paise"]
    assert result["refunded_paise"] == 0


def test_sales_summary_counts_invoices_once_and_only_primary_processed_refunds(staff):
    _, order, headers, _ = approved(staff)
    empty = staff.get("/v1/admin/sales-summary?start=2026-09-11&end=2026-09-11").json()
    assert empty["orders"] == 0 and empty["days"] == []
    payment = start_payment(staff, order, headers)
    capture(payment)
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "UPDATE orders SET invoiced_at='2026-09-10 18:30:00+00' WHERE id=%s", (order["id"],)
        )
        primary = conn.execute(
            "SELECT primary_payment_id FROM orders WHERE id=%s", (order["id"],)
        ).fetchone()[0]
        for amount, status in [(1000, "processed"), (2000, "pending")]:
            conn.execute(
                "INSERT INTO refunds(id,brand_id,order_id,payment_id,amount,status,reason) "
                "VALUES(%s,'patnam-pakodi',%s,%s,%s,%s,'fixture')",
                (uuid.uuid4(), order["id"], primary, amount, status),
            )
    response = staff.get("/v1/admin/sales-summary?start=2026-09-11&end=2026-09-11")
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["orders"] == 1
    assert result["gross_paise"] == order["total_paise"]
    assert result["refunded_paise"] == 1000
    assert result["net_paise"] == order["total_paise"] - 1000
    assert result["days"][0]["day"] == "2026-09-11"
    assert (
        staff.get("/v1/admin/sales-summary?start=2026-09-10&end=2026-09-10").json()["orders"] == 0
    )
    assert staff.get("/v1/admin/sales-summary?start=2026-09-12&end=2026-09-11").status_code == 422
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE orders SET brand_id='other-fixture-brand' WHERE id=%s", (order["id"],))
    assert (
        staff.get("/v1/admin/sales-summary?start=2026-09-11&end=2026-09-11").json()["orders"] == 0
    )


def test_private_media_can_preview_drafts_but_never_other_brands(staff, tmp_path, monkeypatch):
    from PIL import Image

    monkeypatch.setenv("MEDIA_ROOT", str(tmp_path))
    content = io.BytesIO()
    Image.new("RGB", (10, 10), "orange").save(content, format="PNG")
    uploaded = staff.post(
        "/v1/admin/media?alt=Fixture",
        content=content.getvalue(),
        headers={"Content-Type": "image/png"},
    )
    assert uploaded.status_code == 201, uploaded.text
    identifier = uploaded.json()["id"]
    assert staff.get("/v1/media/" + identifier).status_code == 404
    preview = staff.get("/v1/admin/media/" + identifier)
    assert preview.status_code == 200 and preview.headers["content-type"] == "image/webp"
    assert "no-store" in preview.headers["cache-control"]
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE media SET brand_id='other-fixture-brand' WHERE id=%s", (identifier,))
    assert staff.get("/v1/admin/media/" + identifier).status_code == 404
