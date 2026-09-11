"""Hashed credentials and sessions; authenticated encryption for queued data."""

import hashlib
import hmac
import json
import secrets
import time
from contextlib import asynccontextmanager

import psycopg
import pyotp
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from cryptography.fernet import Fernet
from fastapi import HTTPException, Request
from psycopg.rows import dict_row
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import BRAND, app_database_url, origin, setting

PASSWORDS = PasswordHasher()
DUMMY_PASSWORD_HASH = PASSWORDS.hash("unusable-login-timing-placeholder")
LOCAL_KEY = "NDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def seal(value) -> str:
    return (
        Fernet(setting("DATA_ENCRYPTION_KEY", LOCAL_KEY).encode())
        .encrypt(json.dumps(value).encode())
        .decode()
    )


def unseal(value: str):
    return json.loads(
        Fernet(setting("DATA_ENCRYPTION_KEY", LOCAL_KEY).encode()).decrypt(value.encode())
    )


def random_token():
    return secrets.token_urlsafe(32)


@asynccontextmanager
async def connection():
    async with await psycopg.AsyncConnection.connect(
        app_database_url(), row_factory=dict_row, connect_timeout=3
    ) as conn:
        cursor = await conn.execute(
            "SELECT rolsuper,rolbypassrls FROM pg_roles WHERE rolname=current_user"
        )
        role = await cursor.fetchone()
        if role is None or role["rolsuper"] or role["rolbypassrls"]:
            raise RuntimeError("Commerce requires a restricted runtime role")
        await conn.execute("SELECT set_config('app.brand_id',%s,true)", (BRAND,))
        yield conn


async def database():
    async with connection() as conn:
        yield conn


async def one(conn, sql, values=()):
    return await (await conn.execute(sql, values)).fetchone()


async def rows(conn, sql, values=()):
    return await (await conn.execute(sql, values)).fetchall()


async def limit(key: str, maximum: int, seconds: int):
    client = Redis.from_url(
        setting("REDIS_URL", "redis://127.0.0.1:6450/0"),
        socket_connect_timeout=2,
        socket_timeout=2,
    )
    # Atomic sliding window; hashed dimensions avoid phone/reference data in Redis keys.
    script = """
    local t=redis.call('TIME'); local now=tonumber(t[1])*1000+tonumber(t[2])/1000
    redis.call('ZREMRANGEBYSCORE',KEYS[1],0,now-tonumber(ARGV[1])*1000)
    if redis.call('ZCARD',KEYS[1])>=tonumber(ARGV[2]) then return 0 end
    redis.call('ZADD',KEYS[1],now,ARGV[3]); redis.call('EXPIRE',KEYS[1],ARGV[1]); return 1
    """
    try:
        allowed = await client.eval(
            script, 1, "limit:" + digest(key), seconds, maximum, random_token()
        )
        if not allowed:
            raise HTTPException(429, "Too many attempts. Please try again later.")
    except RedisError as error:
        raise HTTPException(503, "Please try again shortly.") from error
    finally:
        await client.aclose()


async def rate_request(request: Request, purpose: str, maximum=20, seconds=60):
    # request.client is direct in development or supplied by the explicitly
    # trusted edge proxy in production. Never parse arbitrary forwarded headers.
    await limit(
        purpose + ":" + (request.client.host if request.client else "unknown"), maximum, seconds
    )


def same_origin(request: Request):
    if request.headers.get("origin") != origin():
        raise HTTPException(403, "Request origin is not allowed")


async def admin(request: Request):
    token = request.cookies.get("pakodi_session", "")
    if not token:
        raise HTTPException(401, "Sign in required")
    async with connection() as conn:
        session = await one(
            conn,
            """SELECT s.*,a.username,a.enrolled FROM sessions s
          JOIN admins a ON a.id=s.admin_id WHERE s.id=%s AND NOT s.revoked
          AND s.expires_at>now() AND a.enabled AND a.enrolled""",
            (digest(token),),
        )
    if not session:
        raise HTTPException(401, "Sign in required")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        same_origin(request)
        if not hmac.compare_digest(
            session["csrf_hash"], digest(request.headers.get("x-csrf-token", ""))
        ):
            raise HTTPException(403, "Reload the page and try again")
    return {"id": str(session["admin_id"]), "username": session["username"]}


def password_valid(encoded: str, password: str):
    try:
        return PASSWORDS.verify(encoded, password)
    except VerificationError:
        return False


def totp_step(secret: str, code: str, previous: int):
    current = int(time.time() // 30)
    generator = pyotp.TOTP(secret)
    for step in (current - 1, current, current + 1):
        if step > previous and hmac.compare_digest(generator.at(step * 30), code):
            return step
    return None
