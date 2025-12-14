import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, UniqueConstraint

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.product_category import ProductCategory
    from app.models.purchase_item import PurchaseItem
    from app.models.sale_item import SaleItem
    from app.models.purchase_return_item import PurchaseReturnItem
    from app.models.sale_return_item import SaleReturnItem
    from app.models.stock_adjustment import StockAdjustment
    from app.models.stock_transfer import StockTransfer


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    unit: str = Field(min_length=1, max_length=50)
    sku: str | None = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
    
    # Additional fields based on project context
    barcode: str | None = Field(default=None, max_length=100)
    internal_code: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    price: Decimal | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=50)


class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    product_category_id: uuid.UUID | None = Field(
        default=None, foreign_key="product_category.id", ondelete="SET NULL"
    )

    # Relationships (temporarily commented out for debugging Alembic issue)
    # organization: "Organization" = Relationship(back_populates="items")
    # created_by: "User" = Relationship()
    # product_category: "ProductCategory" = Relationship(back_populates="items")
    
    # purchase_items: List["PurchaseItem"] = Relationship(back_populates="item")
    # sale_items: List["SaleItem"] = Relationship(back_populates="item")
    # purchase_return_items: List["PurchaseReturnItem"] = Relationship(back_populates="item")
    # sale_return_items: List["SaleReturnItem"] = Relationship(back_populates="item")
    # stock_adjustments: List["StockAdjustment"] = Relationship(back_populates="item")
    # stock_transfers: List["StockTransfer"] = Relationship(back_populates="item")

    __table_args__ = (UniqueConstraint("organization_id", "sku", name="ux_item_organization_sku"),)


class ItemPublic(ItemBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    product_category_id: uuid.UUID | None
    date_created: datetime
    date_updated: datetime


class ItemsPublic(BaseModel):
    data: list[ItemPublic]
    count: int
