"""Integration tests use only a dedicated local Docker fixture database."""

import asyncio
import os
import subprocess
import sys
import uuid
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.types.json import Jsonb

from app.db import LOCAL_MIGRATION_URL
from app.main import app

ROOT = Path(__file__).resolve().parents[1]
OWNER = LOCAL_MIGRATION_URL.rsplit("/", 1)[0] + "/pakodi_mvp_test"
READER = "postgresql://pakodi_reader:local-reader-only@127.0.0.1:54339/pakodi_mvp_test"


def require_fixture_environment():
    prefixes = (
        "DATABASE_",
        "MIGRATION_DATABASE_",
        "COMMERCE_DATABASE_",
        "REDIS_",
        "DATA_ENCRYPTION_",
        "RAZORPAY_",
        "META_",
        "MEDIA_ROOT",
    )
    if any(name.endswith("_FILE") and name.startswith(prefixes) for name in os.environ):
        raise RuntimeError("Unset runtime secret-file overrides before running fixture tests")


@pytest.fixture(scope="session", autouse=True)
def database():
    require_fixture_environment()
    # Deliberately ignore ambient DATABASE_URL: never mutate a configured database.
    with psycopg.connect(LOCAL_MIGRATION_URL, autocommit=True, connect_timeout=3) as conn:
        if not conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = 'pakodi_mvp_test'"
        ).fetchone():
            conn.execute("CREATE DATABASE pakodi_mvp_test")
    environment = {**os.environ, "APP_ENV": "test", "MIGRATION_DATABASE_URL": OWNER}
    for command in (["alembic", "upgrade", "head"], ["app.seed", "--replace"]):
        subprocess.run([sys.executable, "-m", *command], cwd=ROOT, env=environment, check=True)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", READER)
    with TestClient(
        app, backend_options={"loop_factory": asyncio.SelectorEventLoop}
    ) as test_client:
        yield test_client


@pytest.fixture
def insert_record():
    inserted = []

    def insert(kind, payload, *, published=True, brand="patnam-pakodi"):
        slug = "test-" + uuid.uuid4().hex
        with psycopg.connect(OWNER, connect_timeout=3) as conn:
            conn.execute(
                "INSERT INTO content_records (brand_id,kind,slug,published,payload) "
                "VALUES (%s,%s,%s,%s,%s)",
                (brand, kind, slug, published, Jsonb(payload)),
            )
        inserted.append((brand, kind, slug))
        return slug

    yield insert
    with psycopg.connect(OWNER, connect_timeout=3) as conn:
        for key in inserted:
            conn.execute(
                "DELETE FROM content_records WHERE brand_id=%s AND kind=%s AND slug=%s", key
            )
