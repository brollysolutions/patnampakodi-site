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
LAUNCH_PAGES = {"home", "menu", "about-us", "franchise", "contact"}


def launch_records(records: list[dict]) -> list[dict]:
    """Only the explicitly approved editorial records participate in this update."""
    return [
        row
        for row in records
        if row["kind"] in {"brand", "franchise"}
        or (row["kind"] == "page" and row["slug"] in LAUNCH_PAGES)
        or (row["kind"] == "menu" and row["published"])
    ]


def apply_records(connection, records: list[dict], *, replace=False, menu_launch=False):
    selected = launch_records(records) if menu_launch else records
    for record in selected:
        validate_record(record)
    # Transactional and repeatable. Retain old menu payloads and every commerce record.
    if menu_launch:
        connection.execute(
            "UPDATE content_records SET published=false WHERE brand_id=%s AND kind='menu'",
            ("patnam-pakodi",),
        )
    conflict = (
        "DO UPDATE SET payload = EXCLUDED.payload, published = EXCLUDED.published, "
        "position = EXCLUDED.position"
        if replace or menu_launch
        else "DO NOTHING"
    )
    for record in selected:
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
    return len(selected)


def validate_record(record: dict) -> None:
    if record["published"] and record["kind"] in MODELS:
        MODELS[record["kind"]].model_validate(record["payload"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replace", action="store_true", help="Explicitly replace seeded records")
    parser.add_argument(
        "--menu-launch",
        action="store_true",
        help="Apply only the approved four-flavour editorial update; preserve commerce and outlets",
    )
    parser.add_argument(
        "--published-only", action="store_true", help="Load only published source records"
    )
    args = parser.parse_args()
    records = json.loads(SOURCE.read_text(encoding="utf-8"))
    if args.published_only:
        records = [record for record in records if record["published"]]
    with psycopg.connect(migration_url(), connect_timeout=3) as connection:
        count = apply_records(
            connection, records, replace=args.replace, menu_launch=args.menu_launch
        )
    action = (
        "menu launch applied" if args.menu_launch else "replaced" if args.replace else "preserved"
    )
    print(f"Validated and seeded {count} records; existing content {action}.")


if __name__ == "__main__":
    main()
