"""One scoped transaction per request; never trust a client-supplied brand."""

import os
from collections.abc import AsyncIterator

import psycopg
from psycopg.rows import dict_row

from app.config import setting

LOCAL_DATABASE_URL = "postgresql://pakodi_reader:local-reader-only@127.0.0.1:54339/pakodi"
LOCAL_MIGRATION_URL = "postgresql://pakodi_owner:local-owner-only@127.0.0.1:54339/pakodi"


def database_url() -> str:
    configured = setting("DATABASE_URL")
    if os.environ.get("APP_ENV") == "production" and not configured:
        raise RuntimeError("Production database configuration is required")
    return configured or LOCAL_DATABASE_URL


def migration_url() -> str:
    configured = setting("MIGRATION_DATABASE_URL")
    if os.environ.get("APP_ENV") == "production" and not configured:
        raise RuntimeError("Production migration configuration is required")
    return configured or LOCAL_MIGRATION_URL


async def content_connection() -> AsyncIterator[psycopg.AsyncConnection]:
    async with await psycopg.AsyncConnection.connect(
        database_url(), row_factory=dict_row, connect_timeout=3
    ) as connection:
        cursor = await connection.execute(
            "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user"
        )
        role = await cursor.fetchone()
        if role is None or role["rolsuper"] or role["rolbypassrls"]:
            raise RuntimeError("The content API requires a restricted database role")
        await connection.execute("SELECT set_config('app.brand_id', %s, true)", ("patnam-pakodi",))
        yield connection
