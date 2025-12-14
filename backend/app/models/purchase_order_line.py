"""
Purchase Order Line models - редове от поръчки за доставка.
"""

import uuid
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.purchase_order import PurchaseOrder
    from app.models.product import Product


class PurchaseOrderLineBase(BaseModel):
    """Base purchase order line fields."""

    product_id: uuid.UUID = Field(foreign_key="products.id")
    product_code: str = Field(max_length=50, description="Product SKU/code")
    product_name: str = Field(max_length=255, description="Product name")
    description: Optional[str] = Field(
        default=None, max_length=500, description="Line description"
    )

    # Quantities
    quantity: Decimal = Field(
        gt=0, max_digits=15, decimal_places=4, description="Ordered quantity"
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

    # Received quantities
    received_quantity: Decimal = Field(
        default=Decimal("0"),
        max_digits=15,
        decimal_places=4,
        description="Received quantity",
    )
    remaining_quantity: Decimal = Field(
        default=Decimal("0"),
        max_digits=15,
        decimal_places=4,
        description="Remaining quantity to receive",
    )

    # Expected delivery
    expected_delivery_date: Optional[str] = Field(
        default=None, description="Expected delivery date for this line"
    )

    # Notes
    notes: Optional[str] = Field(default=None, max_length=500, description="Line notes")


class PurchaseOrderLine(PurchaseOrderLineBase, table=True):
    """Purchase order line database model."""

    __tablename__ = "purchase_order_lines"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    purchase_order_id: uuid.UUID = Field(foreign_key="purchase_orders.id", index=True)

    # Relationships
    purchase_order: "PurchaseOrder" = Relationship(
        back_populates="purchase_order_lines"
    )
    product: "Product" = Relationship()


class PurchaseOrderLineCreate(PurchaseOrderLineBase):
    """Schema for creating a purchase order line."""

    pass


class PurchaseOrderLineUpdate(SQLModel):
    """Schema for updating a purchase order line."""

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
    received_quantity: Optional[Decimal] = None
    remaining_quantity: Optional[Decimal] = None
    expected_delivery_date: Optional[str] = None
    notes: Optional[str] = None


class PurchaseOrderLinePublic(PurchaseOrderLineBase):
    """Public purchase order line schema."""

    id: uuid.UUID
    purchase_order_id: uuid.UUID
