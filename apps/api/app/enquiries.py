"""Phone-first leads share the existing pipeline, audit and durable notifications."""

import hashlib
import json
import uuid
from pathlib import Path

from fastapi import HTTPException
from psycopg.types.json import Jsonb

from app import commerce
from app.config import BRAND, origin, setting
from app.security import digest, one


def brochure_path():
    configured = setting("BROCHURE_PATH")
    if not configured:
        return None
    path = Path(configured)
    if not path.is_file() or path.stat().st_size > 5_000_000:
        return None
    with path.open("rb") as file:
        if file.read(5) != b"%PDF-":
            return None
    return path


async def create_quick(conn, payload):
    details = {"phone": payload.phone, "purpose": payload.purpose}
    attribution = {key: getattr(payload, key) for key in ("source", "campaign", "medium")}
    fingerprint = hashlib.sha256(
        json.dumps([details, attribution], sort_keys=True).encode()
    ).hexdigest()
    # Serialize only equal retry identifiers; different requests remain independent.
    await conn.execute(
        "SELECT pg_advisory_xact_lock(hashtextextended(%s,0))", (str(payload.request_key),)
    )
    existing = await one(
        conn, "SELECT request_hash FROM enquiries WHERE request_key=%s", (payload.request_key,)
    )
    if existing:
        if existing["request_hash"] != fingerprint:
            raise HTTPException(409, "This request was already used. Please start a new enquiry.")
        return
    identifier = uuid.uuid4()
    await conn.execute(
        "INSERT INTO enquiries(id,brand_id,details,attribution,request_key,request_hash) "
        "VALUES(%s,%s,%s,%s,%s,%s)",
        (identifier, BRAND, Jsonb(details), Jsonb(attribution), payload.request_key, fingerprint),
    )
    settings = await one(conn, "SELECT data FROM settings WHERE brand_id=%s", (BRAND,))
    if settings and settings["data"].get("staff_whatsapp_consent"):
        for phone in settings["data"].get("franchise_recipients", []):
            await commerce.enqueue(
                conn,
                "whatsapp",
                f"enquiry:{identifier}:{digest(phone)}",
                {
                    "phone": phone,
                    "template": "franchise_enquiry_alert_v1",
                    "parameters": [str(identifier), "Not provided", origin() + "/admin/"],
                },
            )
    await commerce.audit(
        conn, "visitor", "enquiry.created", identifier, {"purpose": payload.purpose}
    )
