"""Provision only the generated disposable Docker acceptance database."""

import asyncio
import json
import os
import uuid
from urllib.parse import urlsplit

import psycopg
from psycopg.types.json import Jsonb

from app.admin_cli import provision
from app.config import BRAND, app_database_url


def main():
    parsed = urlsplit(app_database_url())
    database = parsed.path.lstrip("/")
    if (
        os.environ.get("APP_ENV") != "test"
        or os.environ.get("PROVIDER_MODE") != "fixtures"
        or parsed.hostname != "postgres"
        or not database.startswith("pakodi_stage_fixture_")
        or len(database.removeprefix("pakodi_stage_fixture_")) != 12
    ):
        raise RuntimeError("Synthetic records require a generated Docker fixture database")
    suffix = database.removeprefix("pakodi_stage_fixture_")
    if any(char not in "0123456789abcdef" for char in suffix):
        raise RuntimeError("Invalid fixture database identity")
    owner = "postgresql://pakodi_owner:local-owner-only@postgres:5432/" + database
    # Refuse reuse instead of truncating any existing records.
    with psycopg.connect(owner) as conn:
        for table in ["admins", "settings", "variants", "orders", "fulfilment_settings"]:
            if conn.execute("SELECT count(*) FROM " + table).fetchone()[0]:
                raise RuntimeError("Acceptance fixture must be empty")
    asyncio.run(provision("staging-fixture-admin", "synthetic-staging-only-password"))
    business = {
        "legal_name": "Synthetic Fixture Seller",
        "address": "10 Synthetic Seller Street",
        "gstin": "36ABCDE1234F1Z5",
        "state_code": "36",
        "invoice_prefix": "FX",
        "delivery_gst_bps": 1800,
        "franchise_recipients": [],
        "staff_whatsapp_consent": False,
        "approved_for_sales": True,
    }
    product = {
        "slug": "staging-fixture-mix",
        "name": "Staging Fixture Mix",
        "description": "Synthetic acceptance product",
        "price_paise": 11800,
        "dietary": "non-veg",
        "ingredients": "Fixture ingredients",
        "allergens": "Fixture allergens",
        "nutrition": "Fixture nutrition",
        "net_quantity": "100 g",
        "shelf_life": "30 days",
        "manufacturer": "Fixture manufacturer",
        "consumer_care": "Fixture contact",
        "image": "/images/live/pepper-pakodi-ready-mix.webp",
        "category": "fixture-mixes",
        "tags": ["fixture-pepper"],
    }
    identifier = uuid.uuid4()
    with psycopg.connect(owner) as conn:
        conn.execute("UPDATE admins SET enrolled=true WHERE username='staging-fixture-admin'")
        conn.execute("INSERT INTO settings(brand_id,data) VALUES(%s,%s)", (BRAND, Jsonb(business)))
        conn.execute(
            "INSERT INTO variants(id,brand_id,sku,slug,product,price_paise,"
            "gst_bps,hsn,stock,published) "
            "VALUES(%s,%s,'STAGE-FIXTURE','staging-fixture-mix',%s,11800,1800,'2106',10,true)",
            (identifier, BRAND, Jsonb(product)),
        )
        conn.execute(
            "INSERT INTO content_records(brand_id,kind,slug,published,payload) "
            "VALUES(%s,'outlet','staging-fixture-outlet',true,%s)",
            (
                BRAND,
                Jsonb(
                    {
                        "slug": "staging-fixture-outlet",
                        "name": "Synthetic pilot outlet",
                        "city": "Fixture City",
                        "pincode": "500001",
                    }
                ),
            ),
        )
        conn.execute(
            "INSERT INTO variants(id,brand_id,sku,slug,product,price_paise,"
            "gst_bps,hsn,stock,published) VALUES(%s,%s,'STAGE-FRESH',"
            "'staging-fixture-fresh',%s,11800,1800,'2106',10,true)",
            (
                uuid.uuid4(),
                BRAND,
                Jsonb(
                    {
                        **product,
                        "slug": "staging-fixture-fresh",
                        "name": "Staging Fixture Fresh Pakodi",
                        "mode": "fresh",
                        "category": "dry",
                        "outlet_slug": "staging-fixture-outlet",
                        "net_quantity": "1 portion",
                        "shelf_life": "",
                        "manufacturer": "",
                        "image": "/images/live/822655cabe9a63a6.webp",
                    }
                ),
            ),
        )
        conn.execute(
            "INSERT INTO fulfilment_settings(brand_id,data) VALUES(%s,%s)",
            (
                BRAND,
                Jsonb(
                    {
                        "packaged_enabled": True,
                        "fresh_enabled": True,
                        "outlet_slug": "staging-fixture-outlet",
                        "preparation_minutes": 20,
                        "hours": [
                            {"day": day, "opens": "00:00", "closes": "24:00"} for day in range(7)
                        ],
                        "rules": [
                            {
                                "mode": mode,
                                "pincode": "500001",
                                "state_code": "36",
                                "fee_paise": 2000,
                            }
                            for mode in ("fresh", "packaged")
                        ],
                    }
                ),
            ),
        )
    print(json.dumps({"variant": str(identifier)}))


if __name__ == "__main__":
    main()
