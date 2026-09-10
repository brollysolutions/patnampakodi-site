"""Explicit public, private-order and administrator contracts."""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import ConfigDict, Field

from app.schemas import Product, PublicModel


class Address(PublicModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(pattern=r"^\+91[6-9][0-9]{9}$")
    address: str = Field(min_length=10, max_length=500)
    city: str = Field(min_length=2, max_length=100)
    state_code: str = Field(pattern=r"^(0[1-9]|[12][0-9]|3[0-8])$")
    pincode: str = Field(pattern=r"^[1-9][0-9]{5}$")


class CartLine(PublicModel):
    variant_id: UUID
    quantity: int = Field(strict=True, ge=1, le=100)


class OrderRequest(PublicModel):
    request_key: UUID
    customer: Address
    lines: list[CartLine] = Field(min_length=1, max_length=50)
    whatsapp_consent: bool = False


class QuoteLine(PublicModel):
    variant_id: UUID
    sku: str
    name: str
    quantity: int
    price_paise: int
    gst_bps: int
    hsn: str


class OrderView(PublicModel):
    id: UUID
    reference: str
    customer: Address
    lines: list[QuoteLine]
    status: str
    quote_version: int
    quote_expires_at: datetime | None
    delivery_paise: int
    total_paise: int
    tax: dict[str, int]
    invoice_number: str | None
    note: str
    created_at: datetime
    updated_at: datetime
    consent: bool


class RequestReceipt(PublicModel):
    reference: str
    access_token: str
    status: str


class Approve(PublicModel):
    delivery_paise: int = Field(strict=True, ge=0, le=10000000)


class StatusChange(PublicModel):
    status: Literal["declined", "dispatched", "delivered", "delivery_issue"]
    note: str = Field(default="", max_length=500)


class Reason(PublicModel):
    reason: str = Field(min_length=3, max_length=200)


class PaymentStart(PublicModel):
    quote_version: int = Field(gt=0)


class PaymentCheckout(PublicModel):
    key_id: str
    order_id: str
    amount: int
    currency: Literal["INR"] = "INR"


class RefundRequest(Reason):
    amount: int = Field(strict=True, gt=0)


class TrackingRequest(PublicModel):
    reference: str = Field(pattern=r"^PP-[0-9A-HJKMNP-TV-Z]{10}$")
    phone: str = Field(pattern=r"^\+91[6-9][0-9]{9}$")


class TrackingStatus(PublicModel):
    reference: str
    status: str
    updated_at: datetime


class VariantInput(PublicModel):
    sku: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")
    product: Product
    gst_bps: int = Field(strict=True, ge=0, le=4000)
    hsn: str = Field(pattern=r"^[0-9]{4,8}$")
    published: bool = False
    media_id: UUID | None = None


class VariantView(VariantInput):
    id: UUID
    stock: int
    reserved: int


class StockChange(Reason):
    delta: int = Field(strict=True, ge=-1000000, le=1000000)


class BusinessSettings(PublicModel):
    legal_name: str = Field(min_length=2, max_length=150)
    address: str = Field(min_length=10, max_length=500)
    gstin: str = Field(pattern=r"^[0-9]{2}[A-Z0-9]{13}$")
    state_code: str = Field(pattern=r"^(0[1-9]|[12][0-9]|3[0-8])$")
    invoice_prefix: str = Field(pattern=r"^[A-Z]{1,3}$")
    delivery_gst_bps: int = Field(strict=True, ge=0, le=4000)
    franchise_recipients: list[str] = Field(default_factory=list, max_length=10)
    staff_whatsapp_consent: bool = False
    approved_for_sales: bool = False


class Login(PublicModel):
    model_config = ConfigDict(str_strip_whitespace=False)
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=12, max_length=200)
    code: str = Field(min_length=6, max_length=100)


class SessionView(PublicModel):
    username: str
    csrf_token: str


class ActionResult(PublicModel):
    detail: str


class EnquiryInput(PublicModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(pattern=r"^\+91[6-9][0-9]{9}$")
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", max_length=254)
    city: str = Field(min_length=2, max_length=100)
    preferred_model: str = Field(min_length=2, max_length=100)
    budget: str = Field(min_length=1, max_length=100)
    source: str = Field(default="direct", max_length=100)
    campaign: str = Field(default="", max_length=100)
    medium: str = Field(default="", max_length=100)
    website: str = Field(default="", max_length=100)


class EnquiryView(PublicModel):
    id: UUID
    details: dict[str, str]
    attribution: dict[str, str]
    status: str
    created_at: datetime


class QuickEnquiry(PublicModel):
    request_key: UUID
    phone: str = Field(pattern=r"^\+91[6-9][0-9]{9}$")
    purpose: Literal["franchise", "brochure", "contact"] = "franchise"
    source: str = Field(default="direct", max_length=100)
    campaign: str = Field(default="", max_length=100)
    medium: str = Field(default="", max_length=100)
    website: str = Field(default="", max_length=100)


class QuickEnquiryReceipt(ActionResult):
    brochure_url: str | None = None


class EnquiryStatus(PublicModel):
    status: Literal["new", "contacted", "qualified", "won", "lost"]


class MediaView(PublicModel):
    id: UUID
    alt: str
    created_at: datetime


class OutboxView(PublicModel):
    id: UUID
    kind: str
    status: str
    attempts: int
    created_at: datetime
    last_error: str
    overdue: bool


class ReportRow(PublicModel):
    reference: str
    invoice_number: str | None
    created_at: datetime
    total_paise: int
    tax: dict[str, int]
    refunded_paise: int
    invoiced_at: datetime
    lines: list[QuoteLine]
    delivery_paise: int
    state_code: str


class ContentWrite(PublicModel):
    kind: Literal["brand", "page", "menu", "outlet", "franchise"]
    slug: str = Field(pattern=r"^(?:policies/)?[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=100)
    position: int = Field(ge=0, le=10000)
    published: bool
    payload: dict


class ContentView(ContentWrite):
    pass


class OperationCheck(PublicModel):
    name: str
    status: str
    checked_at: datetime
    overdue: bool


class SettlementView(PublicModel):
    id: str
    kind: str
    amount: int
    expected_amount: int | None
    matches: bool


class OperationsView(PublicModel):
    checks: list[OperationCheck]
    settlements: list[SettlementView]


class EnquiryDetails(PublicModel):
    name: str = Field(default="", max_length=100)
    phone: str = Field(pattern=r"^\+91[6-9][0-9]{9}$")
    email: str = Field(default="", pattern=r"^(?:[^\s@]+@[^\s@]+\.[^\s@]+)?$", max_length=254)
    city: str = Field(default="", max_length=100)
    preferred_model: str = Field(default="", max_length=100)
    budget: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=4000)


class SalesDay(PublicModel):
    day: date
    orders: int
    gross_paise: int
    refunded_paise: int
    net_paise: int


class SalesSummary(PublicModel):
    start: date
    end: date
    days: list[SalesDay]
    orders: int
    gross_paise: int
    refunded_paise: int
    net_paise: int
