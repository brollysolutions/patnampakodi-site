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
settlements,message_receipts"""


def main():
    require_fixture_environment()
    if os.environ.get("APP_ENV") != "test":
        raise RuntimeError("Browser fixtures require APP_ENV=test")
    os.environ["COMMERCE_DATABASE_URL"] = APP_DB
    with psycopg.connect(OWNER) as conn:
        conn.execute("TRUNCATE " + TABLES + " RESTART IDENTITY CASCADE")
        conn.execute("DELETE FROM content_records WHERE kind='product'")
    Redis.from_url("redis://127.0.0.1:63799/15").flushdb()
    if sys.argv[1] == "reset":
        return
    _, recovery = run(provision("browser-admin", "a-strong-browser-fixture-password"))
    identifier = uuid.uuid4()
    with psycopg.connect(OWNER) as conn:
        conn.execute("UPDATE admins SET enrolled=true WHERE username='browser-admin'")
        conn.execute("INSERT INTO settings(brand_id,data) VALUES(%s,%s)", (BRAND, Jsonb(BUSINESS)))
        conn.execute(
            """INSERT INTO variants(id,brand_id,sku,slug,product,price_paise,
          gst_bps,hsn,stock,published) VALUES(%s,%s,'BROWSER','fixture-mix',%s,11800,
          1800,'2106',10,true)""",
            (identifier, BRAND, Jsonb(PRODUCT)),
        )
    print(json.dumps({"recovery": recovery[0], "variant": str(identifier)}))


if __name__ == "__main__":
    main()
