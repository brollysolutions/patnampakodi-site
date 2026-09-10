import psycopg
import pytest
from conftest import OWNER, READER
from pydantic import ValidationError

from app.db import database_url, migration_url
from app.schemas import Product


def test_published_storefront_excludes_drafts_and_other_brands(client, insert_record):
    payload = {"slug": "private-marker", "name": "PRIVATE MARKER", "category": "Dry"}
    insert_record("menu", payload, published=False)
    insert_record("menu", payload, brand="another-brand")
    response = client.get("/v1/storefront", headers={"X-Brand-ID": "another-brand"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["pages"]) == 8  # Seven public pages and reusable footer content.
    assert len(data["menu"]) == 51
    assert len(data["outlets"]) == 6
    assert data["products"] == []
    assert "PRIVATE MARKER" not in response.text
    assert '"published":' not in response.text
    assert response.headers["x-robots-tag"] == "noindex, nofollow"
    assert response.headers["cache-control"] == "no-store"


def test_draft_product_and_admin_surface_are_unavailable(client):
    for path in ("/v1/products/unapproved-ready-mix", "/admin", "/docs", "/openapi.json"):
        assert client.get(path).status_code == 404
    assert client.post("/v1/storefront", json={}).status_code == 405


def test_reader_has_no_unscoped_access_and_cannot_write():
    with psycopg.connect(READER, connect_timeout=3) as conn:
        assert conn.execute("SELECT count(*) FROM content_records").fetchone()[0] == 0
        conn.execute("SELECT set_config('app.brand_id', 'patnam-pakodi', true)")
        assert conn.execute("SELECT count(*) FROM content_records").fetchone()[0] == 70
        conn.commit()
        assert conn.execute("SELECT count(*) FROM content_records").fetchone()[0] == 0
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            conn.execute("UPDATE content_records SET published=true")


@pytest.mark.parametrize(
    "missing",
    [
        "ingredients",
        "allergens",
        "nutrition",
        "net_quantity",
        "shelf_life",
        "manufacturer",
        "consumer_care",
    ],
)
def test_database_rejects_incomplete_published_products(insert_record, missing):
    payload = valid_product()
    del payload[missing]
    with pytest.raises(psycopg.errors.CheckViolation):
        insert_record("product", payload)


def valid_product():
    return {
        "slug": "fixture-product",
        "name": "Test fixture",
        "description": "Not for sale",
        "price_paise": 100,
        "dietary": "veg",
        "ingredients": "Fixture ingredients",
        "allergens": "Fixture allergens",
        "nutrition": "Fixture nutrition",
        "net_quantity": "1 g",
        "shelf_life": "1 day",
        "manufacturer": "Test fixture",
        "consumer_care": "Test fixture",
    }


@pytest.mark.parametrize("invalid", [None, "", "   ", 17])
def test_food_information_cannot_be_blank_or_wrong_type(insert_record, invalid):
    payload = {**valid_product(), "allergens": invalid}
    with pytest.raises((psycopg.errors.CheckViolation, psycopg.errors.InvalidParameterValue)):
        insert_record("product", payload)
    with pytest.raises(ValidationError):
        Product.model_validate(payload)


def test_complete_product_can_publish(client, insert_record):
    insert_record("product", valid_product())
    response = client.get("/v1/products/fixture-product")
    assert response.status_code == 200
    assert response.json()["price_paise"] == 100


def test_invalid_public_content_fails_closed(client, insert_record):
    insert_record("menu", {"secret": "do-not-disclose"})
    response = client.get("/v1/storefront")
    assert response.status_code == 503
    assert response.json() == {"detail": "Content is temporarily unavailable"}


def test_privileged_database_role_is_rejected(client, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", OWNER)
    response = client.get("/v1/storefront")
    assert response.status_code == 503
    assert "local-owner" not in response.text


def test_production_never_defaults_to_local_credentials(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MIGRATION_DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError):
        database_url()
    with pytest.raises(RuntimeError):
        migration_url()
