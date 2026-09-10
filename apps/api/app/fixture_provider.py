"""Internal local provider fixture. Never run against real provider accounts."""

import hashlib
import hmac
import json
import os
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Literal

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from app.config import fixture_mode

AUTH = "Basic Zml4dHVyZTpsb2NhbC1maXh0dXJlLW9ubHk="
WEBHOOK_KEY = "local-fixture-webhook-only"


def require_fixture(authorization: Annotated[str, Header()] = ""):
    if not fixture_mode():
        raise HTTPException(404, "Fixture provider is disabled")
    if not hmac.compare_digest(authorization, AUTH):
        raise HTTPException(401, "Fixture authentication required")


app = FastAPI(
    docs_url=None, redoc_url=None, openapi_url=None, dependencies=[Depends(require_fixture)]
)


@contextmanager
def connect():
    path = Path(os.environ.get("FIXTURE_STORE", "/fixtures/provider.sqlite3"))
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=5)
    db.row_factory = sqlite3.Row
    db.execute(
        "CREATE TABLE IF NOT EXISTS objects("
        "id TEXT PRIMARY KEY,kind TEXT NOT NULL,reference TEXT NOT NULL,"
        "payload TEXT NOT NULL,created INTEGER NOT NULL,UNIQUE(kind,reference))"
    )
    try:
        with db:
            yield db
    finally:
        db.close()


def find(db, identifier, kind):
    row = db.execute(
        "SELECT payload FROM objects WHERE id=? AND kind=?", (identifier, kind)
    ).fetchone()
    if not row:
        raise HTTPException(404, "Fixture record not found")
    return json.loads(row["payload"])


def save(db, identifier, kind, reference, payload):
    db.execute(
        "INSERT INTO objects VALUES(?,?,?,?,?)",
        (identifier, kind, reference, json.dumps(payload), int(time.time())),
    )


async def webhook(provider, event, event_id):
    raw = json.dumps(event, separators=(",", ":")).encode()
    signature = hmac.new(WEBHOOK_KEY.encode(), raw, hashlib.sha256).hexdigest()
    headers = {"Content-Type": "application/json"}
    if provider == "razorpay":
        headers.update({"X-Razorpay-Signature": signature, "X-Razorpay-Event-Id": event_id})
    else:
        headers["X-Hub-Signature-256"] = "sha256=" + signature
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "http://api:8000/v1/webhooks/" + provider, content=raw, headers=headers
        )
        response.raise_for_status()


class OrderInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: int = Field(strict=True, gt=0)
    currency: Literal["INR"]
    receipt: uuid.UUID


class RefundInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: int = Field(strict=True, gt=0)
    speed: Literal["normal"]
    receipt: uuid.UUID


class MessageInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    template: str = Field(min_length=1, max_length=100)


@app.get("/health")
def health():
    with connect() as db:
        db.execute("SELECT 1")
    return {"status": "fixture-only"}


@app.post("/v1/orders")
def create_order(payload: OrderInput):
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        existing = db.execute(
            "SELECT payload FROM objects WHERE kind='order' AND reference=?",
            (str(payload.receipt),),
        ).fetchone()
        if existing:
            record = json.loads(existing["payload"])
            if record["amount"] != payload.amount:
                raise HTTPException(409, "Fixture receipt conflict")
            return record
        identifier = "order_fixture_" + uuid.uuid4().hex
        record = {
            "id": identifier,
            "amount": payload.amount,
            "currency": "INR",
            "receipt": str(payload.receipt),
            "status": "created",
        }
        save(db, identifier, "order", str(payload.receipt), record)
        return record


@app.get("/v1/orders")
def orders(receipt: str = "", count: int = Query(default=100, ge=1, le=100)):
    with connect() as db:
        return {
            "items": [
                json.loads(row["payload"])
                for row in db.execute(
                    "SELECT payload FROM objects WHERE kind='order' AND reference=? LIMIT ?",
                    (receipt, count),
                )
            ]
        }


@app.post("/v1/orders/{identifier}/capture")
async def capture(identifier: str):
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        order = find(db, identifier, "order")
        existing = db.execute(
            "SELECT payload FROM objects WHERE kind='payment' AND reference=?", (identifier,)
        ).fetchone()
        if existing:
            payment = json.loads(existing["payload"])
        else:
            payment = {
                "id": "pay_fixture_" + uuid.uuid4().hex,
                "order_id": identifier,
                "amount": order["amount"],
                "currency": "INR",
                "status": "captured",
            }
            save(db, payment["id"], "payment", identifier, payment)
    # Persist before delivery. A retry resends the same signed event identity.
    await webhook(
        "razorpay",
        {"event": "payment.captured", "payload": {"payment": {"entity": payment}}},
        "capture_" + payment["id"],
    )
    return {"detail": "Fixture capture submitted"}


@app.get("/v1/orders/{identifier}/payments")
def payments(identifier: str):
    with connect() as db:
        find(db, identifier, "order")
        return {
            "items": [
                json.loads(row["payload"])
                for row in db.execute(
                    "SELECT payload FROM objects WHERE kind='payment' AND reference=?",
                    (identifier,),
                )
            ]
        }


@app.post("/v1/payments/{identifier}/refund")
def refund(identifier: str, payload: RefundInput, x_refund_idempotency: Annotated[str, Header()]):
    if x_refund_idempotency != str(payload.receipt):
        raise HTTPException(409, "Fixture refund key mismatch")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        payment = find(db, identifier, "payment")
        existing = db.execute(
            "SELECT payload FROM objects WHERE kind='refund' AND reference=?",
            (x_refund_idempotency,),
        ).fetchone()
        if existing:
            record = json.loads(existing["payload"])
            if record["payment_id"] != identifier or record["amount"] != payload.amount:
                raise HTTPException(409, "Fixture refund conflict")
            return record
        refunded = sum(
            json.loads(row["payload"])["amount"]
            for row in db.execute("SELECT payload FROM objects WHERE kind='refund'")
            if json.loads(row["payload"])["payment_id"] == identifier
        )
        if refunded + payload.amount > payment["amount"]:
            raise HTTPException(409, "Fixture refund exceeds captured amount")
        record = {
            "id": "rf_fixture_" + uuid.uuid4().hex,
            "payment_id": identifier,
            "amount": payload.amount,
            "status": "processed",
            "receipt": str(payload.receipt),
        }
        save(db, record["id"], "refund", str(payload.receipt), record)
        return record


@app.get("/v1/refunds/{identifier}")
def get_refund(identifier: str):
    with connect() as db:
        return find(db, identifier, "refund")


@app.get("/v1/settlements/recon/combined")
def settlement(
    year: int,
    month: int = Query(ge=1, le=12),
    count: int = Query(default=1000, ge=1, le=1000),
    skip: int = Query(default=0, ge=0),
):
    from datetime import UTC, datetime

    with connect() as db:
        records = []
        for row in db.execute(
            "SELECT * FROM objects WHERE kind IN ('payment','refund') ORDER BY created,id"
        ):
            created = datetime.fromtimestamp(row["created"], UTC)
            if (created.year, created.month) != (year, month):
                continue
            record = json.loads(row["payload"])
            records.append(
                {
                    "entity_id": record["id"],
                    "type": row["kind"],
                    "amount": record["amount"],
                    "currency": "INR",
                    "fee": 0,
                    "tax": 0,
                    "settlement_id": "setl_fixture",
                }
            )
        return {"items": records[skip : skip + count]}


@app.post("/v1/messages")
async def message(payload: MessageInput):
    identifier = "wamid_fixture_" + uuid.uuid4().hex
    with connect() as db:
        save(
            db, identifier, "message", identifier, {"id": identifier, "template": payload.template}
        )
    await webhook(
        "meta",
        {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {"phone_number_id": "fixture_phone"},
                                "statuses": [{"id": identifier, "status": "delivered"}],
                            }
                        }
                    ]
                }
            ]
        },
        identifier,
    )
    return {"id": identifier}
