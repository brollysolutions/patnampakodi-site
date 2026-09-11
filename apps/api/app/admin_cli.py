"""Interactive administrator provisioning; run only in an authorized terminal."""

import argparse
import asyncio
import getpass
import re
import uuid

from psycopg.types.json import Jsonb

from app.commerce import audit
from app.config import BRAND
from app.security import PASSWORDS, connection, one, seal


async def provision(username, password, recover=False):
    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9._-]{2,63}", username):
        raise ValueError("Use 3-64 letters, digits, dots, underscores or hyphens for the username")
    if not 12 <= len(password) <= 200:
        raise ValueError("Password must contain 12-200 characters")
    async with connection() as conn:
        existing = await one(
            conn, "SELECT id FROM admins WHERE username=%s FOR UPDATE", (username.lower(),)
        )
        if existing and not recover:
            raise ValueError("Account already exists; use recover for an authorized reset")
        if recover and not existing:
            raise ValueError("Account does not exist")
        identifier = existing["id"] if existing else uuid.uuid4()
        await conn.execute(
            """
INSERT INTO
admins(id,brand_id,username,password_hash,totp_secret,recovery_hashes)
VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(id) DO UPDATE SET
password_hash=excluded.password_hash,
totp_secret=excluded.totp_secret,recovery_hashes=excluded.recovery_hashes,enrolled=true,last_totp=-1
""",
            (
                identifier,
                BRAND,
                username.lower(),
                PASSWORDS.hash(password),
                seal(""),
                Jsonb([]),
            ),
        )
        await conn.execute("UPDATE sessions SET revoked=true WHERE admin_id=%s", (identifier,))
        await audit(
            conn, "operator", "admin.recovered" if recover else "admin.created", identifier, {}
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create", "recover"])
    parser.add_argument("username")
    args = parser.parse_args()
    password = getpass.getpass("New password (at least 12 characters): ")
    if not 12 <= len(password) <= 200 or password != getpass.getpass("Repeat password: "):
        raise SystemExit("Passwords did not match or were too short")
    with asyncio.Runner(loop_factory=asyncio.SelectorEventLoop) as runner:
        runner.run(provision(args.username, password, args.action == "recover"))
    print("Administrator account updated. Sign in with the username and password.")


if __name__ == "__main__":
    main()
