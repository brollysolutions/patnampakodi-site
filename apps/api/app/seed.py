"""Load reviewed editorial records. Existing content is preserved by default."""

import argparse
import json
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

from app.db import migration_url
from app.schemas import FranchiseModel, MenuItem, Outlet, Page, Product

MODELS = {
    "page": Page,
    "menu": MenuItem,
    "outlet": Outlet,
    "franchise": FranchiseModel,
    "product": Product,
}
SOURCE = Path(__file__).resolve().parents[1] / "content" / "storefront.json"


def validate_record(record: dict) -> None:
    if record["published"] and record["kind"] in MODELS:
        MODELS[record["kind"]].model_validate(record["payload"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replace", action="store_true", help="Explicitly replace seeded records")
    parser.add_argument(
        "--published-only", action="store_true", help="Load only published source records"
    )
    args = parser.parse_args()
    records = json.loads(SOURCE.read_text(encoding="utf-8"))
    if args.published_only:
        records = [record for record in records if record["published"]]
    for record in records:
        validate_record(record)
    conflict = (
        "DO UPDATE SET payload = EXCLUDED.payload, published = EXCLUDED.published, "
        "position = EXCLUDED.position"
        if args.replace
        else "DO NOTHING"
    )
    with psycopg.connect(migration_url(), connect_timeout=3) as connection:
        for record in records:
            connection.execute(
                "INSERT INTO content_records (brand_id, kind, slug, position, published, payload) "
                "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (brand_id, kind, slug) " + conflict,
                (
                    "patnam-pakodi",
                    record["kind"],
                    record["slug"],
                    record["position"],
                    record["published"],
                    Jsonb(record["payload"]),
                ),
            )
    action = "replaced" if args.replace else "preserved"
    print(f"Validated and seeded {len(records)} records; existing content {action}.")


if __name__ == "__main__":
    main()
