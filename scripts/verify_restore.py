"""Restore synthetic fixture data into a fresh database; never touch configured data."""
from __future__ import annotations

from pathlib import Path
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[1]


def run(*args, capture=False):
    return subprocess.run(["docker", "compose", "exec", "-T", "postgres", *args],
                          cwd=ROOT, check=True, capture_output=capture, text=True)


def main():
    target = "pakodi_restore_fixture_" + uuid.uuid4().hex[:12]
    archive = "/tmp/" + target + ".dump"
    source = "pakodi_mvp_test"
    run("pg_dump", "-U", "pakodi_owner", "-d", source, "-Fc", "-f", archive)
    created = False
    try:
        run("createdb", "-U", "pakodi_owner", target)
        created = True
        run("pg_restore", "-U", "pakodi_owner", "--exit-on-error", "-d", target, archive)
        tables = run("psql", "-U", "pakodi_owner", "-d", source, "-At", "-c",
                     "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;",
                     capture=True).stdout.strip().splitlines()
        if not tables:
            raise RuntimeError("Source fixture has no tables")
        query = "".join('SELECT count(*) FROM public."' + table.replace('"', '""') + '";'
                        for table in tables)
        query += "SELECT version_num FROM alembic_version;"
        original = run("psql", "-U", "pakodi_owner", "-d", source, "-At", "-c", query, capture=True).stdout
        restored = run("psql", "-U", "pakodi_owner", "-d", target, "-At", "-c", query, capture=True).stdout
        if original != restored:
            raise RuntimeError("Restored fixture differs from its source")
        print(f"Fixture pg_dump/pg_restore passed: all {len(tables)} table counts and migration head match")
    finally:
        if created:
            run("dropdb", "-U", "pakodi_owner", target)
        run("rm", "--", archive)


if __name__ == "__main__":
    main()
