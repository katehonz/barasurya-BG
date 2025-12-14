import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.contraagent import Contraagent
    from app.models.organization import Organization
    from app.models.receivable import Receivable
    from app.models.sale_item import SaleItem
    from app.models.sale_return import SaleReturn
    from app.models.store import Store
    from app.models.user import User


class SaleBase(BaseModel):
    date_sale: datetime
    amount: float = Field(default=0, ge=0)
    description: str | None = Field(default=None, max_length=255)


class SaleCreate(SaleBase):
    contraagent_id: uuid.UUID
    store_id: uuid.UUID


class SaleUpdate(SaleBase):
    date_sale: datetime | None = Field(default=0)  # type: ignore
    amount: float | None = Field(default=0, ge=0)  # type: ignore
    contraagent_id: uuid.UUID | None = Field(default=None)  # type: ignore
    store_id: uuid.UUID | None = Field(default=None)  # type: ignore


class Sale(SaleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    contraagent_id: uuid.UUID = Field(
        foreign_key="contraagent.id", nullable=False, ondelete="CASCADE"
    )
    store_id: uuid.UUID = Field(
        foreign_key="store.id", nullable=False, ondelete="CASCADE"
    )

    organization: "Organization" = Relationship(back_populates="sales")
    created_by: "User" = Relationship()
    contraagent: "Contraagent" = Relationship(back_populates="sales")
    store: "Store" = Relationship(back_populates="sales")
    sale_items: list["SaleItem"] = Relationship(
        back_populates="sale", cascade_delete=True
    )
    receivables: list["Receivable"] = Relationship(
        back_populates="sale", cascade_delete=True
    )
    sale_returns: list["SaleReturn"] = Relationship(
        back_populates="sale", cascade_delete=True
    )


class SalePublic(SaleBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    contraagent_id: uuid.UUID
    contraagent_name: str
    store_id: uuid.UUID
    store_name: str
    date_created: datetime
    date_updated: datetime


class SalesPublic(BaseModel):
    data: list[SalePublic]
    count: int
