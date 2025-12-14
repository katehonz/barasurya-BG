import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.purchase import Purchase
    from app.models.sale import Sale
    from app.models.stock_level import StockLevel
    from app.models.stock_transfer import StockTransfer
    from app.models.user import User


class StoreBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    address: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)


class StoreCreate(StoreBase):
    pass


class StoreUpdate(StoreBase):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class Store(StoreBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    organization: "Organization" = Relationship(back_populates="stores")
    created_by: "User" = Relationship()
    purchases: list["Purchase"] = Relationship(
        back_populates="store", cascade_delete=True
    )
    sales: list["Sale"] = Relationship(back_populates="store", cascade_delete=True)
    src_stock_transfers: list["StockTransfer"] = Relationship(
        back_populates="src_store",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[StockTransfer.src_store_id]"},
    )
    dst_stock_transfers: list["StockTransfer"] = Relationship(
        back_populates="dst_store",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[StockTransfer.dst_store_id]"},
    )
    stock_levels: list["StockLevel"] = Relationship(
        back_populates="store", cascade_delete=True
    )


class StorePublic(StoreBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class StoresPublic(BaseModel):
    data: list[StorePublic]
    count: int
