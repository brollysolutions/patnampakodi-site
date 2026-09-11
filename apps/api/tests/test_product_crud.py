"""Saved catalogue discovery and deletion under real fixture RLS/transactions."""

import uuid

import psycopg
import pytest
from conftest import OWNER
from psycopg.types.json import Jsonb
from test_commerce import APP_DB, PRODUCT, add_product, api, request_order, staff  # noqa: F401


def test_product_management_requires_login(api):  # noqa: F811
    assert api.get("/v1/admin/products").status_code == 401
    assert api.delete(f"/v1/admin/variants/{uuid.uuid4()}").status_code == 401


def test_saved_products_include_drafts_and_support_search_filters_and_pages(staff):  # noqa: F811
    first = add_product(staff, suffix="-alpha")
    second = add_product(staff, suffix="-bravo")
    third = add_product(staff, suffix="-charlie")
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE variants SET published=false WHERE id=%s", (second,))
        conn.execute(
            "INSERT INTO variants(id,brand_id,sku,slug,product,price_paise,gst_bps,hsn) "
            "VALUES(%s,'other-brand','FOREIGN','foreign',%s,100,0,'2106')",
            (uuid.uuid4(), Jsonb(PRODUCT)),
        )
    response = staff.get("/v1/admin/products?limit=2")
    assert response.status_code == 200
    page = response.json()
    assert page["total"] == 3
    assert [row["id"] for row in page["items"]] == [first, second]
    assert staff.get("/v1/admin/products?limit=2&offset=2").json()["items"][0]["id"] == third
    assert staff.get("/v1/admin/products?status=draft").json()["items"][0]["id"] == second
    assert staff.get("/v1/admin/products?q=fixture-BRAVO").json()["total"] == 1
    assert staff.get("/v1/admin/products?q=%25").json()["total"] == 0
    assert staff.get("/v1/admin/products?mode=fresh").json()["total"] == 0
    assert staff.get("/v1/admin/products?mode=packaged&status=published").json()["total"] == 2
    assert staff.get("/v1/admin/products?limit=0").status_code == 422


def test_delete_unused_product_unpublishes_content_and_records_audit(staff):  # noqa: F811
    identifier = add_product(staff)
    response = staff.delete(f"/v1/admin/variants/{identifier}")
    assert response.status_code == 200
    assert staff.get("/v1/admin/products").json() == {"items": [], "total": 0}
    assert staff.get("/v1/catalog").json() == []
    with psycopg.connect(OWNER) as conn:
        assert conn.execute(
            "SELECT published FROM content_records WHERE kind='product' AND slug='fixture-mix'"
        ).fetchone() == (False,)
        assert (
            conn.execute(
                "SELECT count(*) FROM audit_events WHERE action='variant.deleted' AND entity=%s",
                (identifier,),
            ).fetchone()[0]
            == 1
        )
    assert staff.delete(f"/v1/admin/variants/{identifier}").status_code == 404


@pytest.mark.parametrize("protected", ["ordered", "reserved"])
def test_delete_preserves_ordered_or_reserved_products(staff, protected):  # noqa: F811
    identifier = add_product(staff)
    if protected == "ordered":
        order, headers, _ = request_order(staff, identifier)
    else:
        with psycopg.connect(OWNER) as conn:
            conn.execute("UPDATE variants SET reserved=1 WHERE id=%s", (identifier,))
    assert staff.delete(f"/v1/admin/variants/{identifier}").status_code == 409
    assert staff.get("/v1/admin/products").json()["total"] == 1
    if protected == "ordered":
        assert staff.get("/v1/order", headers=headers).json()["id"] == order["id"]


def test_delete_requires_csrf_origin_and_matching_brand(staff):  # noqa: F811
    identifier = add_product(staff)
    for headers in ({"x-csrf-token": "wrong"}, {"origin": "https://attacker.invalid"}):
        assert staff.delete(f"/v1/admin/variants/{identifier}", headers=headers).status_code == 403
    foreign = uuid.uuid4()
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "INSERT INTO variants(id,brand_id,sku,slug,product,price_paise,gst_bps,hsn) "
            "VALUES(%s,'other-brand','FOREIGN','foreign',%s,100,0,'2106')",
            (foreign, Jsonb(PRODUCT)),
        )
    assert staff.delete(f"/v1/admin/variants/{foreign}").status_code == 404
    assert staff.get("/v1/admin/products").json()["total"] == 1
    with psycopg.connect(APP_DB) as conn:
        conn.execute("SELECT set_config('app.brand_id','patnam-pakodi',true)")
        assert conn.execute("DELETE FROM variants WHERE id=%s", (foreign,)).rowcount == 0
        assert conn.execute(
            "SELECT has_table_privilege(current_user,'variants','DELETE'), "
            "has_table_privilege(current_user,'orders','DELETE'), "
            "has_table_privilege(current_user,'audit_events','DELETE'), "
            "has_table_privilege(current_user,'content_records','DELETE')"
        ).fetchone() == (True, False, False, False)


def test_delete_holds_checkout_lock_while_checking_order_history(staff, monkeypatch):  # noqa: F811
    from app import product_admin

    identifier = add_product(staff)
    fetch = product_admin.one
    inspected = []

    async def inspect_lock(conn, sql, values):
        if "SELECT EXISTS" in sql:
            with psycopg.connect(OWNER) as competing:
                with pytest.raises(psycopg.errors.LockNotAvailable):
                    competing.execute(
                        "SELECT id FROM variants WHERE id=%s FOR UPDATE NOWAIT", (identifier,)
                    )
            inspected.append(True)
        return await fetch(conn, sql, values)

    monkeypatch.setattr(product_admin, "one", inspect_lock)
    assert staff.delete(f"/v1/admin/variants/{identifier}").status_code == 200
    assert inspected == [True]


def test_update_locks_before_save_to_prevent_delete_recreating_an_id(staff, monkeypatch):  # noqa: F811
    from app import commerce_api

    identifier = add_product(staff)
    save = commerce_api.save_variant

    async def inspect_lock(conn, product_id, payload, actor):
        with psycopg.connect(OWNER) as competing:
            with pytest.raises(psycopg.errors.LockNotAvailable):
                competing.execute(
                    "SELECT id FROM variants WHERE id=%s FOR UPDATE NOWAIT", (product_id,)
                )
        return await save(conn, product_id, payload, actor)

    monkeypatch.setattr(commerce_api, "save_variant", inspect_lock)
    payload = {"sku": "FIXTURE", "product": PRODUCT, "gst_bps": 1800, "hsn": "2106"}
    assert staff.put(f"/v1/admin/variants/{identifier}", json=payload).status_code == 200
