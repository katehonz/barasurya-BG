import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.payable import Payable
    from app.models.purchase_item import PurchaseItem
    from app.models.purchase_return import PurchaseReturn
    from app.models.store import Store
    from app.models.supplier import Supplier
    from app.models.user import User


class PurchaseBase(BaseModel):
    date_purchase: datetime
    amount: float = Field(default=0, ge=0)
    description: str | None = Field(default=None, max_length=255)


class PurchaseCreate(PurchaseBase):
    supplier_id: uuid.UUID
    store_id: uuid.UUID


class PurchaseUpdate(PurchaseBase):
    date_purchase: datetime | None = Field(default=0)  # type: ignore
    amount: float | None = Field(default=0, ge=0)  # type: ignore
    supplier_id: uuid.UUID | None = Field(default=None)  # type: ignore
    store_id: uuid.UUID | None = Field(default=None)  # type: ignore


class Purchase(PurchaseBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    supplier_id: uuid.UUID = Field(
        foreign_key="supplier.id", nullable=False, ondelete="CASCADE"
    )
    store_id: uuid.UUID = Field(
        foreign_key="store.id", nullable=False, ondelete="CASCADE"
    )

    organization: "Organization" = Relationship(back_populates="purchases")
    created_by: "User" = Relationship()
    supplier: "Supplier" = Relationship(back_populates="purchases")
    store: "Store" = Relationship(back_populates="purchases")
    purchase_items: list["PurchaseItem"] = Relationship(
        back_populates="purchase", cascade_delete=True
    )
    payables: list["Payable"] = Relationship(
        back_populates="purchase", cascade_delete=True
    )
    purchase_returns: list["PurchaseReturn"] = Relationship(
        back_populates="purchase", cascade_delete=True
    )


class PurchasePublic(PurchaseBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    supplier_id: uuid.UUID
    supplier_name: str
    store_id: uuid.UUID
    store_name: str
    date_created: datetime
    date_updated: datetime


class PurchasesPublic(BaseModel):
    data: list[PurchasePublic]
    count: int
