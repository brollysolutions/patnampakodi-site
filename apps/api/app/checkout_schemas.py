"""Guest checkout and operator-owned fulfilment configuration."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.commerce_schemas import Address, CartLine, QuoteLine
from app.schemas import PublicModel

Mode = Literal["packaged", "fresh"]


class OpeningWindow(PublicModel):
    day: int = Field(ge=0, le=6, description="Monday=0, Sunday=6; Asia/Kolkata")
    opens: str = Field(pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")
    closes: str = Field(pattern=r"^(?:(?:[01][0-9]|2[0-3]):[0-5][0-9]|24:00)$")

    @model_validator(mode="after")
    def ordered(self):
        if self.opens >= self.closes:
            raise ValueError("Closing time must follow opening time on the same day")
        return self


class DeliveryRule(PublicModel):
    mode: Mode
    pincode: str = Field(pattern=r"^[1-9][0-9]{5}$")
    state_code: str = Field(pattern=r"^(0[1-9]|[12][0-9]|3[0-8])$")
    fee_paise: int = Field(strict=True, ge=0, le=10000000)


class FulfilmentSettings(PublicModel):
    packaged_enabled: bool = False
    fresh_enabled: bool = False
    fresh_paused: bool = False
    outlet_slug: str = Field(default="", pattern=r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*)?$", max_length=100)
    preparation_minutes: int | None = Field(default=None, ge=1, le=240)
    hours: list[OpeningWindow] = Field(default_factory=list, max_length=21)
    rules: list[DeliveryRule] = Field(default_factory=list, max_length=1000)

    @model_validator(mode="after")
    def consistent(self):
        keys = [(rule.mode, rule.pincode) for rule in self.rules]
        if len(keys) != len(set(keys)):
            raise ValueError("Use one delivery rule per shopping mode and PIN code")
        if self.fresh_enabled and (
            not self.outlet_slug or not self.hours or self.preparation_minutes is None
        ):
            raise ValueError("Fresh ordering requires an outlet, hours and preparation estimate")
        for index, window in enumerate(self.hours):
            for other in self.hours[index + 1 :]:
                if (
                    window.day == other.day
                    and window.opens < other.closes
                    and other.opens < window.closes
                ):
                    raise ValueError("Opening windows cannot overlap")
        return self


class Serviceability(PublicModel):
    mode: Mode
    available: bool
    message: str
    delivery_paise: int | None = None
    state_code: str | None = None
    outlet_slug: str = ""
    outlet_name: str = ""
    preparation_minutes: int | None = None
    hours: list[OpeningWindow] = Field(default_factory=list)


class CheckoutQuoteRequest(PublicModel):
    mode: Mode
    customer: Address
    lines: list[CartLine] = Field(min_length=1, max_length=50)


class CheckoutQuote(PublicModel):
    quote_token: str
    expires_at: datetime
    lines: list[QuoteLine]
    delivery_paise: int
    total_paise: int
    tax: dict[str, int]
    fulfilment: Serviceability


class CheckoutOrderRequest(CheckoutQuoteRequest):
    request_key: UUID
    quote_token: str = Field(min_length=20, max_length=4000)
    whatsapp_consent: bool = False
