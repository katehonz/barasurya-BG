"""
Quotation Line models - редове от оферти.
"""

import uuid
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.quotation import Quotation
    from app.models.product import Product


class QuotationLineBase(BaseModel):
    """Base quotation line fields."""

    product_id: uuid.UUID = Field(foreign_key="products.id")
    product_code: str = Field(max_length=50, description="Product SKU/code")
    product_name: str = Field(max_length=255, description="Product name")
    description: Optional[str] = Field(
        default=None, max_length=500, description="Line description"
    )

    # Quantities
    quantity: Decimal = Field(
        gt=0, max_digits=15, decimal_places=4, description="Quoted quantity"
    )
    unit: str = Field(max_length=20, description="Unit of measure")
    unit_price: Decimal = Field(
        ge=0, max_digits=15, decimal_places=2, description="Unit price"
    )

    # Discounts
    discount_percent: Decimal = Field(
        default=Decimal("0"),
        max_digits=5,
        decimal_places=2,
        description="Discount percentage",
    )
    discount_amount: Decimal = Field(
        default=Decimal("0"),
        max_digits=15,
        decimal_places=2,
        description="Discount amount",
    )

    # Taxes
    tax_rate: Decimal = Field(
        default=Decimal("20"), max_digits=5, decimal_places=2, description="VAT rate %"
    )
    tax_amount: Decimal = Field(
        default=Decimal("0"), max_digits=15, decimal_places=2, description="VAT amount"
    )

    # Totals
    line_total: Decimal = Field(
        default=Decimal("0"),
        max_digits=15,
        decimal_places=2,
        description="Line total before tax",
    )
    line_total_with_tax: Decimal = Field(
        default=Decimal("0"),
        max_digits=15,
        decimal_places=2,
        description="Line total with tax",
    )

    # Optional fields for quotations
    optional: bool = Field(default=False, description="Whether this line is optional")
    alternative_product: Optional[str] = Field(
        default=None, max_length=255, description="Alternative product suggestion"
    )

    # Delivery information
    delivery_time: Optional[str] = Field(
        default=None, max_length=100, description="Delivery time for this line"
    )

    # Notes
    notes: Optional[str] = Field(default=None, max_length=500, description="Line notes")


class QuotationLine(QuotationLineBase, table=True):
    """Quotation line database model."""

    __tablename__ = "quotation_lines"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    quotation_id: uuid.UUID = Field(foreign_key="quotations.id", index=True)

    # Relationships
    quotation: "Quotation" = Relationship(back_populates="quotation_lines")
    product: "Product" = Relationship()


class QuotationLineCreate(QuotationLineBase):
    """Schema for creating a quotation line."""

    pass


class QuotationLineUpdate(SQLModel):
    """Schema for updating a quotation line."""

    product_id: Optional[uuid.UUID] = None
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    unit_price: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    line_total: Optional[Decimal] = None
    line_total_with_tax: Optional[Decimal] = None
    optional: Optional[bool] = None
    alternative_product: Optional[str] = None
    delivery_time: Optional[str] = None
    notes: Optional[str] = None


class QuotationLinePublic(QuotationLineBase):
    """Public quotation line schema."""

    id: uuid.UUID
    quotation_id: uuid.UUID
