"""Playwright-only fixture. Hard-coded disposable DB; never ambient data."""

import json
import os
import sys
import uuid

import psycopg
from psycopg.types.json import Jsonb
from redis import Redis

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from conftest import require_fixture_environment  # noqa: E402
from test_commerce import APP_DB, BUSINESS, OWNER, PRODUCT, run  # noqa: E402

from app.admin_cli import provision  # noqa: E402
from app.config import BRAND  # noqa: E402

TABLES = """admins,sessions,variants,orders,order_tokens,payments,refunds,
provider_events,outbox,enquiries,media,settings,invoice_counters,audit_events,
settlements,message_receipts,fulfilment_settings"""


def main():
    require_fixture_environment()
    if os.environ.get("APP_ENV") != "test":
        raise RuntimeError("Browser fixtures require APP_ENV=test")
    os.environ["COMMERCE_DATABASE_URL"] = APP_DB
    with psycopg.connect(OWNER) as conn:
        conn.execute("TRUNCATE " + TABLES + " RESTART IDENTITY CASCADE")
        conn.execute(
            "DELETE FROM content_records WHERE kind='product' OR "
            "(kind='outlet' AND slug='fixture-pilot')"
        )
    Redis.from_url("redis://127.0.0.1:6450/15").flushdb()
    if sys.argv[1] == "reset":
        return
    run(provision("browser-admin", "a-strong-browser-fixture-password"))
    identifier = uuid.uuid4()
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE admins SET enrolled=true WHERE username='browser-admin'")
        conn.execute("INSERT INTO settings(brand_id,data) VALUES(%s,%s)", (BRAND, Jsonb(BUSINESS)))
        conn.execute(
            """INSERT INTO variants(id,brand_id,sku,slug,product,price_paise,
          gst_bps,hsn,stock,published) VALUES(%s,%s,'BROWSER','fixture-mix',%s,11800,
          1800,'2106',10,true)""",
            (
                identifier,
                BRAND,
                Jsonb(
                    {
                        **PRODUCT,
                        "category": "fixture-mixes",
                        "tags": ["fixture-pepper"],
                        "image": "/images/live/pepper-pakodi-ready-mix.webp",
                        "compare_at_price_paise": 15000,
                    }
                ),
            ),
        )
        if sys.argv[1] == "checkout":
            fresh_id = uuid.uuid4()
            conn.execute(
                "INSERT INTO content_records(brand_id,kind,slug,published,payload) "
                "VALUES(%s,'outlet','fixture-pilot',true,%s)",
                (
                    BRAND,
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
            conn.execute(
                "INSERT INTO variants(id,brand_id,sku,slug,product,price_paise,"
                "gst_bps,hsn,stock,published) VALUES(%s,%s,'BROWSER-FRESH',"
                "'fixture-fresh',%s,11800,1800,'2106',20,true)",
                (
                    fresh_id,
                    BRAND,
                    Jsonb(
                        {
                            **PRODUCT,
                            "slug": "fixture-fresh",
                            "name": "Fixture Fresh Pakodi",
                            "mode": "fresh",
                            "category": "dry",
                            "outlet_slug": "fixture-pilot",
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
                            "outlet_slug": "fixture-pilot",
                            "preparation_minutes": 20,
                            "hours": [
                                {"day": day, "opens": "00:00", "closes": "24:00"}
                                for day in range(7)
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
