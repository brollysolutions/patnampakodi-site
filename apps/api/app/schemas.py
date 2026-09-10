"""Public wire models. Editorial provenance and publication flags stay private."""

from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PublicModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_serialization_defaults_required=True,
    )


class Section(PublicModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=20000)


class ContentBlock(PublicModel):
    """Semantic editorial content, never HTML, CSS or executable attributes."""

    kind: Literal[
        "group", "heading", "text", "image", "list", "link", "faq", "icon", "enquiry", "map"
    ]
    record_slug: str = Field(default="", pattern=r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*)?$", max_length=100)
    text: str = Field(default="", max_length=20000)
    title: str = Field(default="", max_length=300)
    href: str = Field(default="", max_length=2000)
    image: str = Field(default="", pattern=r"^(?:/images/live/[a-z0-9-]+\.webp)?$")
    alt: str = Field(default="", max_length=300)
    width: int = Field(default=800, ge=1, le=10000)
    height: int = Field(default=600, ge=1, le=10000)
    level: Literal[1, 2, 3, 4] = 2
    layout: Literal["column", "row"] = "column"
    tone: Literal["none", "cream", "white", "brown"] = "none"
    card: bool = False
    basis: int = Field(default=100, ge=10, le=100)
    items: list[str] = Field(default_factory=list, max_length=100)
    children: list["ContentBlock"] = Field(default_factory=list, max_length=100)

    @field_validator("href")
    @classmethod
    def safe_href(cls, value):
        if not value:
            return value
        if any(ord(c) < 32 for c in value) or "\\" in value:
            raise ValueError("Invalid link")
        parsed = urlsplit(value)
        if value.startswith("/") and not value.startswith("//"):
            return value
        if parsed.scheme in {"https", "mailto", "tel"}:
            return value
        raise ValueError("Use a local, HTTPS, phone or email link")


class Page(PublicModel):
    slug: str = Field(pattern=r"^(?:policies/)?[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=500)
    heading: str = Field(min_length=1, max_length=200)
    intro: str = Field(min_length=1, max_length=20000)
    sections: list[Section] = Field(default_factory=list)
    blocks: list[ContentBlock] = Field(default_factory=list, max_length=100)

    @field_validator("blocks")
    @classmethod
    def bounded_blocks(cls, blocks):
        pending = [(block, 1) for block in blocks]
        count = 0
        while pending:
            block, depth = pending.pop()
            count += 1
            if depth > 16 or count > 2000:
                raise ValueError("Page content exceeds the supported size")
            pending.extend((child, depth + 1) for child in block.children)
        return blocks


class MenuItem(PublicModel):
    slug: str
    name: str
    category: Literal["Dry", "Wet", "Bowls", "Dips", "Drinks"]
    description: str = ""
    dietary: Literal["veg", "non-veg", "unconfirmed"] = "unconfirmed"
    price_paise: int | None = Field(default=None, ge=0)
    featured: bool = False


class Outlet(PublicModel):
    slug: str
    name: str
    city: str
    pincode: str = Field(pattern=r"^[1-9][0-9]{5}$")
    address: str | None = None
    hours: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    phone: str | None = Field(default=None, pattern=r"^\+[1-9][0-9]{7,14}$")


class FranchiseModel(PublicModel):
    name: str
    description: str
    image: Literal["display", "cart", "cabin", "shop"]
    investment_paise: int | None = Field(default=None, gt=0)


class Product(PublicModel):
    # Optional discovery metadata never substitutes for the required food facts.
    category: str = Field(default="", pattern=r"^(?:[a-z0-9]+(?:-[a-z0-9]+)*)?$", max_length=80)
    tags: list[Annotated[str, Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=80)]] = Field(
        default_factory=list, max_length=20
    )
    image: str = Field(default="", pattern=r"^(?:/images/live/[a-z0-9-]+\.webp)?$")
    compare_at_price_paise: int | None = Field(default=None, gt=0, le=100000000)

    @model_validator(mode="after")
    def valid_reference_price(self):
        if (
            self.compare_at_price_paise is not None
            and self.compare_at_price_paise < self.price_paise
        ):
            raise ValueError("Original price must be at least the current price")
        if len(set(self.tags)) != len(self.tags):
            raise ValueError("Product tags must be unique")
        return self

    # Every food/identity field is required before publication.
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    price_paise: int = Field(gt=0, le=100000000)
    dietary: Literal["veg", "non-veg"]
    ingredients: str = Field(min_length=1)
    allergens: str = Field(min_length=1)
    nutrition: str = Field(min_length=1)
    net_quantity: str = Field(min_length=1)
    shelf_life: str = Field(min_length=1)
    manufacturer: str = Field(min_length=1)
    consumer_care: str = Field(min_length=1)


class Storefront(PublicModel):
    brand: Literal["Patnam Pakodi"] = "Patnam Pakodi"
    tagline: str
    revision: str
    pages: list[Page]
    menu: list[MenuItem]
    outlets: list[Outlet]
    franchise_models: list[FranchiseModel]
    products: list[Product]
    contact_email: str | None = None
    contact_phone: str | None = None


class Health(PublicModel):
    status: Literal["ok"] = "ok"
