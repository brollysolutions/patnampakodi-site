"""Public wire models. Editorial provenance and publication flags stay private."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PublicModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        json_schema_serialization_defaults_required=True,
    )


class Section(PublicModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=20000)


class Page(PublicModel):
    slug: str = Field(pattern=r"^(?:policies/)?[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=500)
    heading: str = Field(min_length=1, max_length=200)
    intro: str = Field(min_length=1, max_length=20000)
    sections: list[Section] = Field(default_factory=list)


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
    # Every field is required before a product can enter the public response.
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
