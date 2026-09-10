"""Operator-only first deployment role provisioning; never logs credentials."""

from urllib.parse import unquote, urlsplit

import psycopg
from psycopg import sql

from app.config import setting
from app.db import migration_url


def main():
    with psycopg.connect(migration_url()) as conn:
        for key, expected in (
            ("DATABASE_URL", "pakodi_reader"),
            ("COMMERCE_DATABASE_URL", "pakodi_app"),
        ):
            parsed = urlsplit(setting(key))
            if parsed.username != expected or not parsed.password:
                raise ValueError("A named restricted database role and password are required")
            if conn.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (expected,)).fetchone():
                raise RuntimeError("Role already exists; use the documented rotation procedure")
            conn.execute(
                sql.SQL("CREATE ROLE {} LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD {}").format(
                    sql.Identifier(expected), sql.Literal(unquote(parsed.password))
                )
            )
            conn.execute(
                sql.SQL("GRANT USAGE ON SCHEMA public TO {}").format(sql.Identifier(expected))
            )
    print("Restricted runtime roles provisioned")


if __name__ == "__main__":
    main()
