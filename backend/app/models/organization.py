import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.account_transaction import AccountTransaction
    from app.models.customer import Customer
    from app.models.customer_type import CustomerType
    from app.models.invoice import Invoice
    from app.models.item import Item
    from app.models.item_category import ItemCategory
    from app.models.item_unit import ItemUnit
    from app.models.organization_member import OrganizationMember
    from app.models.payable import Payable
    from app.models.payment import Payment
    from app.models.permission import Permission
    from app.models.purchase import Purchase
    from app.models.purchase_return import PurchaseReturn
    from app.models.receivable import Receivable
    from app.models.role import Role
    from app.models.sale import Sale
    from app.models.sale_return import SaleReturn
    from app.models.stock_adjustment import StockAdjustment
    from app.models.stock_transfer import StockTransfer
    from app.models.store import Store
    from app.models.supplier import Supplier


class OrganizationBase(BaseModel):
    name: str = Field(min_length=1, max_length=255, index=True)
    slug: str = Field(min_length=1, max_length=100, unique=True, index=True)
    is_active: bool = True


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None


class Organization(OrganizationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    members: list["OrganizationMember"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    items: list["Item"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    item_categories: list["ItemCategory"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    item_units: list["ItemUnit"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    stores: list["Store"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    suppliers: list["Supplier"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    customer_types: list["CustomerType"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    customers: list["Customer"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    purchases: list["Purchase"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    sales: list["Sale"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    accounts: list["Account"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    account_transactions: list["AccountTransaction"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    payments: list["Payment"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    stock_adjustments: list["StockAdjustment"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    stock_transfers: list["StockTransfer"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    payables: list["Payable"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    receivables: list["Receivable"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    sale_returns: list["SaleReturn"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    purchase_returns: list["PurchaseReturn"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    roles: list["Role"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    permissions: list["Permission"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    invoices: list["Invoice"] = Relationship(
        back_populates="organization", cascade_delete=True
    )


class OrganizationPublic(OrganizationBase):
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class OrganizationsPublic(BaseModel):
    data: list[OrganizationPublic]
    count: int
