"""HTTP authorization and explicit contracts; business transitions live in services."""

import csv
import hashlib
import hmac
import io
import json
import os
import uuid
from datetime import date
from typing import Annotated

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, PlainTextResponse
from PIL import Image, UnidentifiedImageError
from psycopg.types.json import Jsonb
from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from app import commerce
from app.commerce_schemas import (
    ActionResult,
    Approve,
    BusinessSettings,
    ContentView,
    ContentWrite,
    EnquiryInput,
    EnquiryStatus,
    EnquiryView,
    Login,
    MediaView,
    OperationsView,
    OrderRequest,
    OrderView,
    OutboxView,
    PaymentCheckout,
    PaymentStart,
    RefundRequest,
    ReportRow,
    RequestReceipt,
    SessionView,
    StatusChange,
    StockChange,
    TrackingRequest,
    TrackingStatus,
    VariantInput,
    VariantView,
)
from app.config import BRAND, media_root, origin, setting
from app.schemas import FranchiseModel, MenuItem, Outlet, Page
from app.security import (
    DUMMY_PASSWORD_HASH,
    admin,
    database,
    digest,
    limit,
    one,
    password_valid,
    random_token,
    rate_request,
    rows,
    same_origin,
    seal,
    totp_step,
    unseal,
)

router = APIRouter(prefix="/v1")
DB = Annotated[psycopg.AsyncConnection, Depends(database)]
Admin = Annotated[dict, Depends(admin)]


def bearer(request):
    value = request.headers.get("authorization", "")
    if not value.startswith("Bearer ") or len(value) > 200:
        raise HTTPException(404, "Order link is unavailable")
    return value[7:]


async def private_order(request, conn, write=False):
    await rate_request(request, "order-access", 120)
    if write:
        same_origin(request)
    return await commerce.order_by_token(conn, bearer(request), lock=write)


def variant_view(record):
    return VariantView(
        id=record["id"],
        sku=record["sku"],
        product=record["product"],
        gst_bps=record["gst_bps"],
        hsn=record["hsn"],
        published=record["published"],
        media_id=record["media_id"],
        stock=record["stock"],
        reserved=record["reserved"],
    )


@router.get("/catalog", response_model=list[VariantView])
async def catalog(conn: DB):
    return [
        variant_view(row)
        for row in await rows(conn, "SELECT * FROM variants WHERE published ORDER BY slug")
    ]


@router.post("/orders", response_model=RequestReceipt, status_code=201)
async def create_order(payload: OrderRequest, request: Request, conn: DB):
    same_origin(request)
    await rate_request(request, "request-order", 20)
    await limit("order-phone:" + payload.customer.phone, 5, 3600)
    order, token = await commerce.create_request(conn, payload)
    return RequestReceipt(reference=order["reference"], access_token=token, status=order["status"])


@router.get("/order", response_model=OrderView)
async def get_order(request: Request, conn: DB):
    return commerce.view(await private_order(request, conn))


@router.put("/order", response_model=OrderView)
async def revise_order(payload: OrderRequest, request: Request, conn: DB):
    order = await private_order(request, conn, True)
    if order["status"] not in {"requested", "approved"}:
        raise HTTPException(409, "This order can no longer be edited")
    lines = await commerce.snapshot(conn, payload.lines)
    updated = await one(
        conn,
        """
UPDATE orders SET customer=%s,lines=%s,status='requested',consent=%s,
quote_version=quote_version+1,quote_expires_at=NULL,total_paise=0,delivery_paise=0,tax='{}',
updated_at=now() WHERE id=%s RETURNING *
""",
        (Jsonb(payload.customer.model_dump()), Jsonb(lines), payload.whatsapp_consent, order["id"]),
    )
    await commerce.audit(
        conn, "customer", "request.revised", order["id"], {"approval_invalidated": True}
    )
    return commerce.view(updated)


@router.post("/order/payment", response_model=PaymentCheckout)
async def pay(payload: PaymentStart, request: Request, conn: DB):
    if not setting("RAZORPAY_KEY_ID"):
        raise HTTPException(503, "Payments are not yet available. Your request is saved.")
    order = await private_order(request, conn, True)
    payment = await commerce.begin_payment(conn, order, payload.quote_version)
    return PaymentCheckout(
        key_id=setting("RAZORPAY_KEY_ID"),
        order_id=payment["provider_order"] or "",
        amount=payment["amount"],
    )


@router.post("/order/cancel", response_model=OrderView)
async def cancel(request: Request, conn: DB):
    return commerce.view(
        await commerce.cancel(conn, await private_order(request, conn, True), "customer")
    )


@router.post("/order/opt-out", response_model=ActionResult)
async def opt_out(request: Request, conn: DB):
    order = await private_order(request, conn, True)
    await conn.execute("UPDATE orders SET consent=false WHERE id=%s", (order["id"],))
    await commerce.audit(conn, "customer", "consent.revoked", order["id"], {})
    return ActionResult(detail="WhatsApp updates stopped")


@router.post("/tracking", response_model=TrackingStatus)
async def track(payload: TrackingRequest, request: Request, conn: DB):
    same_origin(request)
    await rate_request(request, "tracking-minute", 5)
    await rate_request(request, "tracking-hour", 30, 3600)
    await limit("tracking-phone:" + payload.phone, 20, 3600)
    await limit("tracking-reference:" + payload.reference, 5, 1800)
    record = await one(
        conn,
        """
SELECT reference,status,updated_at,customer->>'phone' AS phone FROM orders
WHERE reference=%s
""",
        (payload.reference,),
    )
    if not record or not hmac.compare_digest(record["phone"], payload.phone):
        raise HTTPException(404, "We could not find a matching order")
    return TrackingStatus(
        reference=record["reference"], status=record["status"], updated_at=record["updated_at"]
    )


@router.get("/order/invoice")
async def invoice(request: Request, conn: DB):
    order = await private_order(request, conn)
    if not order["invoice_number"]:
        raise HTTPException(409, "The invoice is available after payment confirmation")
    from app.invoices import invoice_pdf

    return Response(
        invoice_pdf(order),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="invoice.pdf"'},
    )


@router.post("/enquiries", response_model=ActionResult, status_code=201)
async def enquiry(payload: EnquiryInput, request: Request, conn: DB):
    same_origin(request)
    await rate_request(request, "enquiry", 5, 3600)
    await limit("enquiry-phone:" + payload.phone, 3, 3600)
    if payload.website:
        raise HTTPException(422, "Please check your enquiry details")
    identifier = uuid.uuid4()
    details = payload.model_dump(exclude={"source", "campaign", "medium", "website"})
    attribution = {"source": payload.source, "campaign": payload.campaign, "medium": payload.medium}
    await conn.execute(
        "INSERT INTO enquiries(id,brand_id,details,attribution) VALUES(%s,%s,%s,%s)",
        (identifier, BRAND, Jsonb(details), Jsonb(attribution)),
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
                    "parameters": [str(identifier), payload.city, origin() + "/admin/"],
                },
            )
    await commerce.audit(conn, "visitor", "enquiry.created", identifier, {})
    return ActionResult(detail="Your enquiry is saved. Our team will contact you.")


@router.post("/admin/login", response_model=SessionView)
async def login(payload: Login, request: Request, response: Response, conn: DB):
    same_origin(request)
    await rate_request(request, "login", 30)
    await limit("login-user:" + payload.username.lower(), 5, 300)
    account = await one(
        conn,
        "SELECT * FROM admins WHERE username=%s AND enabled FOR UPDATE",
        (payload.username.lower(),),
    )
    valid = await run_in_threadpool(
        password_valid,
        account["password_hash"] if account else DUMMY_PASSWORD_HASH,
        payload.password,
    )
    if not account or not valid:
        raise HTTPException(401, "Sign-in details were not accepted")
    step = totp_step(unseal(account["totp_secret"]), payload.code, account["last_totp"])
    recovery = list(account["recovery_hashes"])
    if step is None:
        match = next(
            (code for code in recovery if hmac.compare_digest(code, digest(payload.code))), None
        )
        if not match or not account["enrolled"]:
            raise HTTPException(401, "Sign-in details were not accepted")
        recovery.remove(match)
        step = account["last_totp"]
    await conn.execute(
        "UPDATE admins SET enrolled=true,last_totp=%s,recovery_hashes=%s WHERE id=%s",
        (step, Jsonb(recovery), account["id"]),
    )
    token, csrf = random_token(), random_token()
    await conn.execute(
        """
INSERT INTO sessions(id,brand_id,admin_id,csrf_hash,expires_at)
VALUES(%s,%s,%s,%s,now()+interval '8 hours')
""",
        (digest(token), BRAND, account["id"], digest(csrf)),
    )
    secure = os.environ.get("APP_ENV") == "production"
    response.set_cookie(
        "pakodi_session",
        token,
        httponly=True,
        secure=secure,
        samesite="strict",
        max_age=28800,
        path="/",
    )
    response.set_cookie(
        "pakodi_csrf",
        csrf,
        httponly=False,
        secure=secure,
        samesite="strict",
        max_age=28800,
        path="/",
    )
    await commerce.audit(conn, str(account["id"]), "session.created", account["id"], {})
    return SessionView(username=account["username"], csrf_token=csrf)


@router.get("/admin/session", response_model=SessionView)
async def session(request: Request, actor: Admin):
    return SessionView(
        username=actor["username"], csrf_token=request.cookies.get("pakodi_csrf", "")
    )


@router.post("/admin/logout", response_model=ActionResult)
async def logout(request: Request, response: Response, conn: DB, actor: Admin):
    await conn.execute(
        "UPDATE sessions SET revoked=true WHERE id=%s",
        (digest(request.cookies.get("pakodi_session", "")),),
    )
    response.delete_cookie("pakodi_session")
    response.delete_cookie("pakodi_csrf")
    return ActionResult(detail="Signed out")


@router.get("/admin/orders", response_model=list[OrderView])
async def orders(
    conn: DB,
    actor: Admin,
    search: str = Query(default="", max_length=100),
    offset: int = Query(default=0, ge=0),
):
    result = await rows(
        conn,
        """
SELECT * FROM orders WHERE reference ILIKE %s OR customer->>'phone'=%s ORDER
BY created_at DESC LIMIT 100 OFFSET %s
""",
        ("%" + search + "%", search, offset),
    )
    return [commerce.view(order) for order in result]


@router.post("/admin/orders/{order_id}/approve", response_model=OrderView)
async def approve_order(order_id: uuid.UUID, payload: Approve, conn: DB, actor: Admin):
    return commerce.view(
        await commerce.approve(conn, order_id, payload.delivery_paise, actor["id"])
    )


@router.post("/admin/orders/{order_id}/status", response_model=OrderView)
async def status_order(order_id: uuid.UUID, payload: StatusChange, conn: DB, actor: Admin):
    return commerce.view(await commerce.set_status(conn, order_id, payload, actor["id"]))


@router.post("/admin/orders/{order_id}/cancel", response_model=OrderView)
async def cancel_order(order_id: uuid.UUID, conn: DB, actor: Admin):
    return commerce.view(
        await commerce.cancel(conn, await commerce.order_by_id(conn, order_id), actor["id"])
    )


@router.post("/admin/orders/{order_id}/refund", response_model=ActionResult)
async def refund_order(order_id: uuid.UUID, payload: RefundRequest, conn: DB, actor: Admin):
    await commerce.refund(
        conn,
        await commerce.order_by_id(conn, order_id),
        payload.amount,
        payload.reason,
        actor["id"],
    )
    return ActionResult(detail="Refund requested; provider confirmation is pending")


@router.get("/admin/orders/{order_id}/invoice")
async def admin_invoice(order_id: uuid.UUID, conn: DB, actor: Admin):
    order = await commerce.order_by_id(conn, order_id, False)
    if not order["invoice_number"]:
        raise HTTPException(409, "Invoice is not available")
    from app.invoices import invoice_pdf

    return Response(
        invoice_pdf(order),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="invoice.pdf"'},
    )


@router.post("/admin/orders/{order_id}/recover-link", response_model=RequestReceipt)
async def recover_link(order_id: uuid.UUID, conn: DB, actor: Admin):
    order = await commerce.order_by_id(conn, order_id)
    await conn.execute("UPDATE order_tokens SET revoked=true WHERE order_id=%s", (order_id,))
    await commerce.audit(
        conn, actor["id"], "order.link-recovered", order_id, {"previous_links_revoked": True}
    )
    return RequestReceipt(
        reference=order["reference"],
        access_token=await commerce.token_for(conn, order_id),
        status=order["status"],
    )


@router.get("/admin/variants", response_model=list[VariantView])
async def variants(conn: DB, actor: Admin):
    return [
        variant_view(row)
        for row in await rows(conn, "SELECT * FROM variants ORDER BY sku LIMIT 1000")
    ]


async def save_variant(conn, identifier, payload, actor):
    if payload.media_id and not await one(
        conn, "SELECT id FROM media WHERE id=%s", (payload.media_id,)
    ):
        raise HTTPException(422, "Select an existing image")
    previous = await one(conn, "SELECT * FROM variants WHERE id=%s FOR UPDATE", (identifier,))
    if previous and previous["slug"] != payload.product.slug:
        raise HTTPException(
            409, "Published product paths are permanent; create a new variant instead"
        )
    record = await one(
        conn,
        """
INSERT INTO
variants(id,brand_id,sku,slug,product,price_paise,gst_bps,hsn,published,media_id)
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(id) DO UPDATE SET
sku=excluded.sku,
product=excluded.product,price_paise=excluded.price_paise,gst_bps=excluded.gst_bps,hsn=excluded.hsn,
published=excluded.published,media_id=excluded.media_id RETURNING *
""",
        (
            identifier,
            BRAND,
            payload.sku,
            payload.product.slug,
            Jsonb(payload.product.model_dump()),
            payload.product.price_paise,
            payload.gst_bps,
            payload.hsn,
            payload.published,
            payload.media_id,
        ),
    )
    await conn.execute(
        """
INSERT INTO content_records(brand_id,kind,slug,published,payload)
VALUES(%s,'product',%s,%s,%s)
ON CONFLICT(brand_id,kind,slug) DO UPDATE SET
published=excluded.published,payload=excluded.payload
""",
        (BRAND, payload.product.slug, payload.published, Jsonb(payload.product.model_dump())),
    )
    await commerce.audit(
        conn,
        actor,
        "variant.saved",
        identifier,
        {
            "published": payload.published,
            "price_before": previous["price_paise"] if previous else None,
            "price_after": payload.product.price_paise,
        },
    )
    return variant_view(record)


@router.post("/admin/variants", response_model=VariantView, status_code=201)
async def create_variant(payload: VariantInput, conn: DB, actor: Admin):
    return await save_variant(conn, uuid.uuid4(), payload, actor["id"])


@router.put("/admin/variants/{identifier}", response_model=VariantView)
async def update_variant(identifier: uuid.UUID, payload: VariantInput, conn: DB, actor: Admin):
    if not await one(conn, "SELECT id FROM variants WHERE id=%s", (identifier,)):
        raise HTTPException(404, "Product not found")
    return await save_variant(conn, identifier, payload, actor["id"])


@router.post("/admin/variants/{identifier}/stock", response_model=VariantView)
async def stock(identifier: uuid.UUID, payload: StockChange, conn: DB, actor: Admin):
    previous = await one(conn, "SELECT stock FROM variants WHERE id=%s FOR UPDATE", (identifier,))
    record = await one(
        conn,
        """
UPDATE variants SET stock=stock+%s WHERE id=%s AND stock+%s>=reserved
RETURNING *
""",
        (payload.delta, identifier, payload.delta),
    )
    if not record:
        raise HTTPException(
            409, "Adjustment would consume reserved stock or product is unavailable"
        )
    await commerce.audit(
        conn,
        actor["id"],
        "stock.adjusted",
        identifier,
        {"before": previous["stock"], "after": record["stock"], "reason": payload.reason},
    )
    return variant_view(record)


CSV_FIELDS = [
    "sku",
    "slug",
    "name",
    "description",
    "price_paise",
    "dietary",
    "ingredients",
    "allergens",
    "nutrition",
    "net_quantity",
    "shelf_life",
    "manufacturer",
    "consumer_care",
    "gst_bps",
    "hsn",
    "published",
]


@router.get("/admin/products.csv")
async def export_products(conn: DB, actor: Admin):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for row in await rows(conn, "SELECT * FROM variants ORDER BY sku"):
        data = {
            **row["product"],
            "sku": row["sku"],
            "gst_bps": row["gst_bps"],
            "hsn": row["hsn"],
            "published": str(row["published"]).lower(),
        }
        writer.writerow(
            {
                key: (
                    "'" + str(data[key])
                    if str(data[key]).startswith("'")
                    or str(data[key]).lstrip().startswith(("=", "+", "-", "@"))
                    else data[key]
                )
                for key in CSV_FIELDS
            }
        )
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="products.csv"'},
    )


@router.post("/admin/products.csv", response_model=ActionResult)
async def import_products(request: Request, conn: DB, actor: Admin):
    try:
        text = (await request.body()).decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        if reader.fieldnames != CSV_FIELDS:
            raise ValueError("Use the exported column headings")
        imported = list(reader)
        if not 1 <= len(imported) <= 1000:
            raise ValueError("Import between 1 and 1000 products")
        for row in imported:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("CSV row width does not match the header")
            for key, value in row.items():
                if value.startswith("'") and (
                    value[1:].startswith("'") or value[1:].lstrip().startswith(("=", "+", "-", "@"))
                ):
                    row[key] = value[1:]
            if row["published"] not in {"true", "false"}:
                raise ValueError("published must be true or false")
            product = {
                key: row[key]
                for key in CSV_FIELDS
                if key not in {"sku", "gst_bps", "hsn", "published"}
            }
            product["price_paise"] = int(product["price_paise"])
            payload = VariantInput(
                sku=row["sku"],
                product=product,
                gst_bps=int(row["gst_bps"]),
                hsn=row["hsn"],
                published=row["published"] == "true",
            )
            existing = await one(
                conn, "SELECT id,media_id FROM variants WHERE sku=%s", (payload.sku,)
            )
            if existing:
                payload.media_id = existing["media_id"]
            await save_variant(
                conn, existing["id"] if existing else uuid.uuid4(), payload, actor["id"]
            )
    except (ValueError, UnicodeError, ValidationError, csv.Error) as error:
        raise HTTPException(
            422, "CSV was not imported. Check its columns and product fields."
        ) from error
    return ActionResult(detail=f"Imported {len(imported)} products")


@router.get("/admin/settings", response_model=BusinessSettings | None)
async def get_settings(conn: DB, actor: Admin):
    record = await one(conn, "SELECT data FROM settings WHERE brand_id=%s", (BRAND,))
    return record["data"] if record else None


@router.put("/admin/settings", response_model=BusinessSettings)
async def put_settings(payload: BusinessSettings, conn: DB, actor: Admin):
    import re

    if not payload.gstin.startswith(payload.state_code) or any(
        not re.fullmatch(r"\+91[6-9][0-9]{9}", phone) for phone in payload.franchise_recipients
    ):
        raise HTTPException(422, "Check seller state and recipient phone numbers")
    await conn.execute(
        """
INSERT INTO settings(brand_id,data) VALUES(%s,%s) ON CONFLICT(brand_id) DO
UPDATE SET data=excluded.data
""",
        (BRAND, Jsonb(payload.model_dump())),
    )
    await commerce.audit(
        conn,
        actor["id"],
        "settings.updated",
        BRAND,
        {"approved_for_sales": payload.approved_for_sales},
    )
    return payload


@router.get("/admin/enquiries", response_model=list[EnquiryView])
async def list_enquiries(conn: DB, actor: Admin, offset: int = Query(default=0, ge=0)):
    return [
        EnquiryView.model_validate({key: row[key] for key in EnquiryView.model_fields})
        for row in await rows(
            conn, "SELECT * FROM enquiries ORDER BY created_at DESC LIMIT 100 OFFSET %s", (offset,)
        )
    ]


@router.post("/admin/enquiries/{identifier}/status", response_model=ActionResult)
async def enquiry_status(identifier: uuid.UUID, payload: EnquiryStatus, conn: DB, actor: Admin):
    previous = await one(conn, "SELECT status FROM enquiries WHERE id=%s FOR UPDATE", (identifier,))
    if not previous:
        raise HTTPException(404, "Enquiry not found")
    await conn.execute("UPDATE enquiries SET status=%s WHERE id=%s", (payload.status, identifier))
    await commerce.audit(
        conn,
        actor["id"],
        "enquiry.status",
        identifier,
        {"before": previous["status"], "after": payload.status},
    )
    return ActionResult(detail="Enquiry updated")


@router.get("/admin/messages", response_model=list[OutboxView])
async def messages(conn: DB, actor: Admin, offset: int = Query(default=0, ge=0)):
    result = await rows(
        conn,
        """
SELECT *,kind='whatsapp' AND status NOT IN ('delivered','suppressed')
AND created_at<now()-interval '10 minutes' AS overdue FROM outbox ORDER BY
created_at DESC LIMIT 200 OFFSET %s
""",
        (offset,),
    )
    return [
        OutboxView.model_validate({key: row[key] for key in OutboxView.model_fields})
        for row in result
    ]


@router.get("/admin/operations", response_model=OperationsView)
async def operations(conn: DB, actor: Admin):
    checks = await rows(
        conn,
        """SELECT name,status,checked_at,
      checked_at<now()-CASE WHEN name='worker' THEN interval '2 minutes'
      ELSE interval '26 hours' END AS overdue FROM operation_checks ORDER BY name""",
    )
    transactions = await rows(
        conn,
        """
      SELECT s.id,s.payload->>'type' AS kind,(s.payload->>'amount')::int AS amount,
      COALESCE(p.amount,r.amount) AS expected_amount,
      COALESCE((s.payload->>'amount')::int=COALESCE(p.amount,r.amount)
      AND s.payload->>'currency'='INR',false) AS matches
      FROM settlements s LEFT JOIN payments p ON s.payload->>'type'='payment'
      AND p.provider_payment=s.id LEFT JOIN refunds r ON s.payload->>'type'='refund'
      AND r.provider_id=s.id ORDER BY s.fetched_at DESC LIMIT 1000
    """,
    )
    return {"checks": checks, "settlements": transactions}


@router.post("/admin/messages/{identifier}/retry", response_model=ActionResult)
async def retry(identifier: uuid.UUID, conn: DB, actor: Admin):
    record = await one(
        conn,
        """
UPDATE outbox SET status='pending',attempts=0,due_at=now() WHERE id=%s AND
status='failed' RETURNING id
""",
        (identifier,),
    )
    if not record:
        raise HTTPException(409, "Only failed jobs can be retried")
    await commerce.audit(conn, actor["id"], "job.retried", identifier, {})
    return ActionResult(detail="Retry scheduled")


@router.get("/admin/gst-report", response_model=list[ReportRow])
async def gst_report(conn: DB, actor: Admin, start: date, end: date):
    if end < start or (end - start).days > 366:
        raise HTTPException(422, "Select a period of up to one year")
    result = await rows(
        conn,
        """
SELECT o.*,customer->>'state_code' AS state_code,
COALESCE((SELECT sum(r.amount) FROM refunds r WHERE
r.order_id=o.id
AND r.payment_id=o.primary_payment_id AND r.status='processed'),0)::int
AS refunded_paise FROM orders o WHERE
invoice_number IS NOT NULL
AND invoiced_at >= (%s::date::timestamp AT TIME ZONE 'Asia/Kolkata')
AND invoiced_at < ((%s::date+1)::timestamp AT TIME ZONE 'Asia/Kolkata')
ORDER BY invoiced_at
""",
        (start, end),
    )
    return [
        ReportRow.model_validate({key: row[key] for key in ReportRow.model_fields})
        for row in result
    ]


@router.get("/admin/gst-report.csv")
async def gst_csv(conn: DB, actor: Admin, start: date, end: date):
    records = await gst_report(conn, actor, start, end)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Invoice",
            "Issued UTC",
            "Order",
            "State",
            "SKU",
            "HSN",
            "Quantity",
            "Unit paise",
            "GST basis points",
            "Order total paise",
            "Delivery paise",
            "CGST paise",
            "SGST paise",
            "IGST paise",
            "Processed refund paise",
        ]
    )
    for order in records:
        for line in order.lines:
            writer.writerow(
                [
                    order.invoice_number,
                    order.invoiced_at.isoformat(),
                    order.reference,
                    order.state_code,
                    "'" + line.sku,
                    line.hsn,
                    line.quantity,
                    line.price_paise,
                    line.gst_bps,
                    order.total_paise,
                    order.delivery_paise,
                    order.tax["cgst"],
                    order.tax["sgst"],
                    order.tax["igst"],
                    order.refunded_paise,
                ]
            )
    return Response(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="gst-ledger.csv"'},
    )


@router.get("/admin/content", response_model=list[ContentView])
async def list_content(conn: DB, actor: Admin):
    return await rows(
        conn,
        """
SELECT kind,slug,position,published,payload FROM content_records WHERE
kind!='product' ORDER BY kind,position
""",
    )


@router.put("/admin/content", response_model=ContentView)
async def save_content(payload: ContentWrite, conn: DB, actor: Admin):
    if payload.kind != "page" and "/" in payload.slug:
        raise HTTPException(422, "Only policy pages use a nested URL")
    if payload.kind in {"page", "menu", "outlet"} and payload.payload.get("slug") != payload.slug:
        raise HTTPException(422, "Content URL must match its record slug")
    models = {"page": Page, "menu": MenuItem, "outlet": Outlet, "franchise": FranchiseModel}
    try:
        if payload.kind in models:
            models[payload.kind].model_validate(payload.payload)
        elif not {"tagline", "revision"} <= payload.payload.keys() or set(payload.payload) - {
            "tagline",
            "revision",
            "contact_email",
            "contact_phone",
        }:
            raise ValueError("Invalid brand fields")
        if payload.kind == "brand":
            from app.schemas import Storefront

            Storefront.model_validate(
                {
                    **payload.payload,
                    "pages": [],
                    "menu": [],
                    "outlets": [],
                    "franchise_models": [],
                    "products": [],
                }
            )
    except (ValidationError, ValueError) as error:
        raise HTTPException(422, "Content fields are not valid") from error
    await conn.execute(
        """
INSERT INTO content_records(brand_id,kind,slug,position,published,payload)
VALUES(%s,%s,%s,%s,%s,%s)
ON CONFLICT(brand_id,kind,slug) DO UPDATE SET
position=excluded.position,published=excluded.published,payload=excluded.payload
""",
        (
            BRAND,
            payload.kind,
            payload.slug,
            payload.position,
            payload.published,
            Jsonb(payload.payload),
        ),
    )
    await commerce.audit(
        conn,
        actor["id"],
        "content.saved",
        payload.slug,
        {"kind": payload.kind, "published": payload.published},
    )
    return payload


@router.get("/admin/media", response_model=list[MediaView])
async def list_media(conn: DB, actor: Admin):
    return await rows(
        conn, "SELECT id,alt,created_at FROM media ORDER BY created_at DESC LIMIT 1000"
    )


@router.post("/admin/media", response_model=MediaView, status_code=201)
async def upload_media(
    request: Request, conn: DB, actor: Admin, alt: str = Query(min_length=1, max_length=300)
):
    raw = await request.body()
    Image.MAX_IMAGE_PIXELS = 16000000
    try:
        image = Image.open(io.BytesIO(raw))
        if image.format not in {"JPEG", "PNG", "WEBP"} or image.width * image.height > 16000000:
            raise ValueError("Unsupported image")
        image.load()
        image = image.convert("RGB")
        image.thumbnail((2400, 2400))
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as error:
        raise HTTPException(422, "Upload a JPEG, PNG, or WebP image up to 16 megapixels") from error
    identifier = uuid.uuid4()
    root = media_root()
    root.mkdir(parents=True, exist_ok=True)
    image.save(root / (str(identifier) + ".webp"), "WEBP", quality=85)
    record = await one(
        conn,
        "INSERT INTO media(id,brand_id,alt) VALUES(%s,%s,%s) RETURNING id,alt,created_at",
        (identifier, BRAND, alt),
    )
    await commerce.audit(conn, actor["id"], "media.created", identifier, {})
    return record


@router.get("/media/{identifier}")
async def public_media(identifier: uuid.UUID, conn: DB):
    if not await one(
        conn, "SELECT id FROM variants WHERE media_id=%s AND published LIMIT 1", (identifier,)
    ):
        raise HTTPException(404, "Image not found")
    path = media_root() / (str(identifier) + ".webp")
    if not path.is_file():
        raise HTTPException(404, "Image not found")
    return FileResponse(path, media_type="image/webp")


@router.get("/webhooks/meta", response_class=PlainTextResponse)
async def meta_verify(request: Request):
    expected = setting("META_VERIFY_TOKEN")
    if (
        not expected
        or request.query_params.get("hub.mode") != "subscribe"
        or not hmac.compare_digest(request.query_params.get("hub.verify_token", ""), expected)
    ):
        raise HTTPException(403, "Verification failed")
    return request.query_params.get("hub.challenge", "")


@router.post("/webhooks/{provider}", response_model=ActionResult)
async def webhook(provider: str, request: Request, conn: DB):
    if provider not in {"razorpay", "meta"}:
        raise HTTPException(404, "Not found")
    raw = await request.body()
    secret = setting("RAZORPAY_WEBHOOK_SECRET" if provider == "razorpay" else "META_APP_SECRET")
    header = request.headers.get(
        "x-razorpay-signature" if provider == "razorpay" else "x-hub-signature-256", ""
    )
    expected = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    if provider == "meta":
        expected = "sha256=" + expected
    if not secret or not hmac.compare_digest(expected, header):
        raise HTTPException(400, "Invalid signature")
    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError()
    except ValueError as error:
        raise HTTPException(400, "Invalid event") from error
    if provider == "razorpay":
        event_id = request.headers.get("x-razorpay-event-id", "")
        if not event_id or len(event_id) > 200 or not isinstance(data.get("event"), str):
            raise HTTPException(400, "Invalid event")
        event_id = "razorpay:" + event_id
        inserted = await one(
            conn,
            """
INSERT INTO provider_events(id,brand_id,provider,payload)
VALUES(%s,%s,%s,%s) ON CONFLICT(id) DO NOTHING RETURNING id
""",
            (event_id, BRAND, provider, seal(data)),
        )
        if inserted:
            await commerce.enqueue(conn, "razorpay_event", event_id, {"event_id": event_id})
    else:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if value.get("metadata", {}).get("phone_number_id") != setting("META_PHONE_ID"):
                    continue
                for status in value.get("statuses", []):
                    state = status.get("status")
                    if state in {"delivered", "read", "failed"} and status.get("id"):
                        await conn.execute(
                            """
INSERT INTO message_receipts(id,brand_id,status) VALUES(%s,%s,%s)
ON CONFLICT(id) DO UPDATE SET status=excluded.status,received_at=now()
WHERE message_receipts.status!='delivered'
""",
                            (status["id"], BRAND, "failed" if state == "failed" else "delivered"),
                        )
                for message in value.get("messages", []):
                    if message.get("text", {}).get("body", "").strip().upper() in {
                        "STOP",
                        "UNSUBSCRIBE",
                    }:
                        phone = "+" + str(message.get("from", "")).lstrip("+")
                        await conn.execute(
                            "UPDATE orders SET consent=false WHERE customer->>'phone'=%s", (phone,)
                        )
        from app.jobs import apply_receipts

        await apply_receipts(conn)
    return ActionResult(detail="Accepted")
