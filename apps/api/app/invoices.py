"""PDF generated only from the immutable paid order snapshot."""

from datetime import timedelta
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.commerce import tax_amount


def invoice_pdf(order):
    output = BytesIO()
    doc = SimpleDocTemplate(output)
    styles = getSampleStyleSheet()

    def p(text):
        return Paragraph(escape(str(text)), styles["Normal"])

    seller = order["seller"]
    customer = order["customer"]
    flow = [
        Paragraph("Tax invoice", styles["Title"]),
        p(order["invoice_number"]),
        p(
            "Issued: "
            + (order["invoiced_at"] + timedelta(hours=5, minutes=30)).strftime("%d %b %Y")
        ),
        p(seller["legal_name"]),
        p(seller["address"]),
        p("GSTIN: " + seller["gstin"]),
        Spacer(1, 16),
        p("Order: " + order["reference"]),
        p(customer["name"]),
        p(customer["address"] + ", " + customer["city"] + " " + customer["pincode"]),
        p("Place of supply (state code): " + customer["state_code"]),
        p("Reverse charge: No"),
        Spacer(1, 16),
    ]
    data = [["Product / HSN", "Qty", "Unit INR", "GST %", "Tax INR", "Gross INR"]]
    for line in order["lines"]:
        data.append(
            [
                p(line["name"] + " / " + line["hsn"]),
                str(line["quantity"]),
                f"{line['price_paise'] / 100:.2f}",
                f"{line['gst_bps'] / 100:g}",
                f"{tax_amount(line['quantity'] * line['price_paise'], line['gst_bps']) / 100:.2f}",
                f"{line['quantity'] * line['price_paise'] / 100:.2f}",
            ]
        )
    table = Table(data, colWidths=[175, 30, 65, 50, 70, 80], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FBEFD9")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    flow.extend([table, Spacer(1, 16), p(f"Delivery INR {order['delivery_paise'] / 100:.2f}")])
    flow.append(p(f"Delivery GST rate {seller['delivery_gst_bps'] / 100:g}%"))
    for key in ("taxable", "cgst", "sgst", "igst"):
        flow.append(p(f"{key.upper()} INR {order['tax'][key] / 100:.2f}"))
    flow.extend(
        [p(f"Total paid INR {order['total_paise'] / 100:.2f}"), p("Prices include applicable tax.")]
    )
    doc.build(flow)
    return output.getvalue()
