import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.payable import Payable
    from app.models.purchase import Purchase
    from app.models.purchase_return import PurchaseReturn
    from app.models.user import User


class SupplierBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=255)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(SupplierBase):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class Supplier(SupplierBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    organization: "Organization" = Relationship(back_populates="suppliers")
    created_by: "User" = Relationship()
    purchases: list["Purchase"] = Relationship(
        back_populates="supplier", cascade_delete=True
    )
    payables: list["Payable"] = Relationship(
        back_populates="supplier", cascade_delete=True
    )
    purchase_returns: list["PurchaseReturn"] = Relationship(
        back_populates="supplier", cascade_delete=True
    )


class SupplierPublic(SupplierBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class SuppliersPublic(BaseModel):
    data: list[SupplierPublic]
    count: int
