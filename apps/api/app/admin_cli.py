"""Interactive administrator provisioning; run only in an authorized terminal."""

import argparse
import asyncio
import getpass
import re
import uuid

import pyotp
from psycopg.types.json import Jsonb

from app.commerce import audit
from app.config import BRAND
from app.security import PASSWORDS, connection, digest, one, random_token, seal


async def provision(username, password, recover=False):
    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9._-]{2,63}", username):
        raise ValueError("Use 3-64 letters, digits, dots, underscores or hyphens for the username")
    if not 12 <= len(password) <= 200:
        raise ValueError("Password must contain 12-200 characters")
    secret = pyotp.random_base32()
    recovery_codes = [random_token() for _ in range(10)]
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
totp_secret=excluded.totp_secret,recovery_hashes=excluded.recovery_hashes,enrolled=false,last_totp=-1
""",
            (
                identifier,
                BRAND,
                username.lower(),
                PASSWORDS.hash(password),
                seal(secret),
                Jsonb([digest(code) for code in recovery_codes]),
            ),
        )
        await conn.execute("UPDATE sessions SET revoked=true WHERE admin_id=%s", (identifier,))
        await audit(
            conn, "operator", "admin.recovered" if recover else "admin.created", identifier, {}
        )
    return secret, recovery_codes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create", "recover"])
    parser.add_argument("username")
    args = parser.parse_args()
    password = getpass.getpass("New password (at least 12 characters): ")
    if not 12 <= len(password) <= 200 or password != getpass.getpass("Repeat password: "):
        raise SystemExit("Passwords did not match or were too short")
    with asyncio.Runner(loop_factory=asyncio.SelectorEventLoop) as runner:
        secret, codes = runner.run(provision(args.username, password, args.action == "recover"))
    print("Enter this setup key in your authenticator app:", secret)
    print("Save these single-use recovery codes in your password manager:")
    print("\n".join(codes))
    print("Sign in with the password and authenticator code to finish enrollment.")


if __name__ == "__main__":
    main()
