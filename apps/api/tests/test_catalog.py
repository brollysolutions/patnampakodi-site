"""Catalog publication, filter validation and CSV metadata regression tests."""

import asyncio
import csv
import io

import psycopg
from conftest import OWNER
from fastapi.testclient import TestClient
from test_commerce import PRODUCT, add_product

from app.main import app

pytest_plugins = ["test_commerce"]


def test_source_catalog_is_complete_private_and_keeps_sale_data_unset(staff):
    from app.catalog_drafts import CONTENT, source_catalog

    with TestClient(app, backend_options={"loop_factory": asyncio.SelectorEventLoop}) as anonymous:
        assert anonymous.get("/v1/admin/catalog-drafts").status_code == 401
    assert len(source_catalog()) == 58
    drafts = staff.get("/v1/admin/catalog-drafts").json()
    assert len(drafts) == 58
    assert sum(item["mode"] == "packaged" for item in drafts) == 4
    assert sum(item["mode"] == "fresh" for item in drafts) == 54
    assert len({item["sku"] for item in drafts}) == len(drafts)
    assert len({item["slug"] for item in drafts}) == len(drafts)
    assert "pachi-mirchi-kodi-pakodi" in {item["slug"] for item in drafts}
    assert "pachi-mirchi-chicken-pakodi" not in {item["slug"] for item in drafts}
    images = {item["slug"]: item["image"] for item in drafts}
    assert images["blue-lagoon-mojito"] == images["cheese-dip"] == ""
    assert images["chettinadu-pakodi-ready-mix"].endswith("chettinadu-pakodi-ready-mix.webp")
    assert images["pachi-mirchi-kodi-pakodi"]
    for item in drafts:
        assert not {"price_paise", "stock", "gst_bps", "ingredients", "allergens"} & item.keys()
        if item["image"]:
            assert (CONTENT.parents[1] / "web" / "public" / item["image"].lstrip("/")).is_file()
    assert staff.get("/v1/catalog").json() == []
    # A source entry cannot be posted directly to bypass the existing food/tax validation.
    assert staff.post("/v1/admin/variants", json={"product": drafts[0]}).status_code == 422


def test_completed_source_entry_is_hidden_without_overwriting_stock_or_crossing_brands(staff):
    draft = next(
        item for item in staff.get("/v1/admin/catalog-drafts").json() if item["mode"] == "packaged"
    )
    product = {**PRODUCT, **{key: value for key, value in draft.items() if key != "sku"}}
    product["description"] = PRODUCT["description"]
    product["dietary"] = "veg"  # Synthetic test facts, not source product approval.
    created = staff.post(
        "/v1/admin/variants",
        json={
            "sku": draft["sku"],
            "product": product,
            "gst_bps": 1800,
            "hsn": "2106",
            "published": False,
        },
    )
    assert created.status_code == 201, created.text
    identifier = created.json()["id"]
    assert (
        staff.post(
            f"/v1/admin/variants/{identifier}/stock",
            json={
                "delta": 7,
                "reason": "Synthetic test stock",
            },
        ).status_code
        == 200
    )
    for _ in range(2):
        assert draft["slug"] not in {
            item["slug"] for item in staff.get("/v1/admin/catalog-drafts").json()
        }
        row = next(
            item for item in staff.get("/v1/admin/variants").json() if item["id"] == identifier
        )
        assert row["stock"] == 7 and not row["published"]
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "UPDATE variants SET brand_id='other-fixture-brand' WHERE id=%s", (identifier,)
        )
    assert draft["slug"] in {item["slug"] for item in staff.get("/v1/admin/catalog-drafts").json()}


def update(staff, identifier, **changes):
    current = next(row for row in staff.get("/v1/admin/variants").json() if row["id"] == identifier)
    payload = {
        key: current[key] for key in ("sku", "product", "gst_bps", "hsn", "published", "media_id")
    }
    payload["product"] = {**payload["product"], **changes}
    response = staff.put("/v1/admin/variants/" + identifier, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_catalog_filters_are_combined_literal_and_publication_scoped(staff):
    first = add_product(staff, suffix="-first")
    second = add_product(staff, suffix="-second")
    update(
        staff,
        first,
        name="Pepper 100% Mix",
        category="ready-mixes",
        tags=["pepper"],
        price_paise=20000,
    )
    update(
        staff, second, name="Chilli Mix", category="ready-mixes", tags=["chilli"], price_paise=10000
    )
    assert [
        r["id"] for r in staff.get("/v1/catalog?q=100%25&category=ready-mixes&tag=pepper").json()
    ] == [first]
    assert staff.get("/v1/catalog?q=100%25&tag=chilli").json() == []
    assert [r["id"] for r in staff.get("/v1/catalog?sort=price-asc").json()] == [second, first]
    assert [r["id"] for r in staff.get("/v1/catalog?sort=price-desc").json()] == [first, second]
    assert [r["id"] for r in staff.get("/v1/catalog?max_price=10000").json()] == [second]
    assert staff.get("/v1/catalog", params={"q": "' OR true --"}).json() == []
    assert staff.get("/v1/catalog?max_price=-1").status_code == 422
    assert staff.get("/v1/catalog?sort=stock").status_code == 422
    assert staff.get("/v1/catalog", params={"q": "x" * 101}).status_code == 422
    current = update(staff, first)
    payload = {key: current[key] for key in ("sku", "product", "gst_bps", "hsn", "media_id")}
    assert (
        staff.put("/v1/admin/variants/" + first, json={**payload, "published": False}).status_code
        == 200
    )
    assert staff.get("/v1/catalog?tag=pepper").json() == []


def test_catalog_metadata_survives_csv_roundtrip_and_legacy_import(staff):
    identifier = add_product(staff)
    update(
        staff,
        identifier,
        category="ready-mixes",
        tags=["pepper", "spicy"],
        compare_at_price_paise=15000,
        image="/images/live/956c6f3fefa9428c.webp",
    )
    exported = staff.get("/v1/admin/products.csv").text
    assert (
        staff.post(
            "/v1/admin/products.csv", content=exported, headers={"Content-Type": "text/csv"}
        ).status_code
        == 200
    )
    product = staff.get("/v1/catalog").json()[0]["product"]
    assert product["tags"] == ["pepper", "spicy"]
    assert product["compare_at_price_paise"] == 15000
    assert product["image"].endswith(".webp")
    reader = csv.DictReader(io.StringIO(exported))
    legacy = [
        key
        for key in reader.fieldnames
        if key not in {"category", "tags", "compare_at_price_paise", "image", "mode", "outlet_slug"}
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, legacy, extrasaction="ignore")
    writer.writeheader()
    # Match the SKU normalization used by the typed editor before preserving metadata.
    for row in reader:
        row["sku"] = " " + row["sku"] + " "
        writer.writerow(row)
    assert (
        staff.post(
            "/v1/admin/products.csv",
            content=output.getvalue(),
            headers={"Content-Type": "text/csv"},
        ).status_code
        == 200
    )
    assert staff.get("/v1/catalog").json()[0]["product"] == product


def test_catalog_metadata_rejects_invalid_values_and_preserves_brand_isolation(staff):
    identifier = add_product(staff)
    current = staff.get("/v1/admin/variants").json()[0]
    payload = {
        key: current[key] for key in ("sku", "product", "gst_bps", "hsn", "published", "media_id")
    }
    for changes in (
        {"compare_at_price_paise": 1},
        {"tags": ["pepper", "pepper"]},
        {"image": "https://example.invalid/image.webp"},
        {"category": "../private"},
    ):
        response = staff.put(
            "/v1/admin/variants/" + identifier,
            json={**payload, "product": {**payload["product"], **changes}},
        )
        assert response.status_code == 422
    # The fixed application brand cannot discover a different brand, even when
    # its published product exactly matches every requested filter.
    with psycopg.connect(OWNER) as conn:
        conn.execute(
            "UPDATE variants SET brand_id='other-fixture-brand' WHERE id=%s", (identifier,)
        )
    assert staff.get("/v1/catalog?q=Fixture").json() == []
    assert staff.get("/v1/admin/variants").json() == []
