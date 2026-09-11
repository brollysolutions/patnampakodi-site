"""Staff reporting under request-scoped authorization and brand isolation."""

import csv
import io

from fastapi import HTTPException
from psycopg.types.json import Jsonb

from app import commerce
from app.security import one, rows


def valid_period(start, end):
    if end < start or (end - start).days > 366:
        raise HTTPException(422, "Select a period of up to one year")


async def enrich_enquiry(conn, identifier, payload, actor):
    previous = await one(
        conn, "SELECT details FROM enquiries WHERE id=%s FOR UPDATE", (identifier,)
    )
    if not previous:
        raise HTTPException(404, "Enquiry not found")
    details = {**previous["details"], **payload.model_dump(exclude_unset=True)}
    updated = await one(
        conn,
        "UPDATE enquiries SET details=%s WHERE id=%s "
        "RETURNING id,details,attribution,status,created_at",
        (Jsonb(details), identifier),
    )
    await commerce.audit(
        conn, actor, "enquiry.enriched", identifier, {"fields": sorted(payload.model_fields_set)}
    )
    return updated


async def enquiry_csv(conn, start, end, status):
    valid_period(start, end)
    result = await rows(
        conn,
        """SELECT * FROM enquiries WHERE
      created_at >= (%s::date::timestamp AT TIME ZONE 'Asia/Kolkata')
      AND created_at < ((%s::date+1)::timestamp AT TIME ZONE 'Asia/Kolkata')
      AND (%s='' OR status=%s) ORDER BY created_at,id LIMIT 10001""",
        (start, end, status, status),
    )
    if len(result) > 10000:
        raise HTTPException(
            422, "Too many enquiries to export. Select a shorter period or one status."
        )
    output = io.StringIO()
    writer = csv.writer(output)
    detail_fields = [
        "name",
        "phone",
        "email",
        "city",
        "preferred_model",
        "budget",
        "purpose",
        "notes",
    ]
    attribution_fields = ["source", "campaign", "medium"]
    writer.writerow(["Created UTC", "Status", *detail_fields, *attribution_fields])
    for record in result:
        # Literal cells also cover leading whitespace and control characters.
        cells = ["'" + str(record["details"].get(key, "")) for key in detail_fields]
        cells += ["'" + str(record["attribution"].get(key, "")) for key in attribution_fields]
        writer.writerow([record["created_at"].isoformat(), record["status"], *cells])
    return output.getvalue()


async def sales_summary(conn, start, end):
    valid_period(start, end)
    days = await rows(
        conn,
        """WITH sales AS (
      SELECT (o.invoiced_at AT TIME ZONE 'Asia/Kolkata')::date AS day,
        o.total_paise AS gross_paise,
        COALESCE((SELECT sum(r.amount) FROM refunds r WHERE r.order_id=o.id
          AND r.payment_id=o.primary_payment_id AND r.status='processed'),0) AS refunded_paise
      FROM orders o WHERE o.invoice_number IS NOT NULL
        AND o.invoiced_at >= (%s::date::timestamp AT TIME ZONE 'Asia/Kolkata')
        AND o.invoiced_at < ((%s::date+1)::timestamp AT TIME ZONE 'Asia/Kolkata')
    ) SELECT day,count(*) AS orders,sum(gross_paise) AS gross_paise,
      sum(refunded_paise) AS refunded_paise,sum(gross_paise-refunded_paise) AS net_paise
      FROM sales GROUP BY day ORDER BY day""",
        (start, end),
    )
    fields = ["orders", "gross_paise", "refunded_paise", "net_paise"]
    normalized = [{"day": row["day"], **{key: int(row[key]) for key in fields}} for row in days]
    return {
        "start": start,
        "end": end,
        "days": normalized,
        **{key: sum(row[key] for row in normalized) for key in fields},
    }
