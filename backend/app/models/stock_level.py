import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.item import Item
    from app.models.store import Store
    from app.models.user import User


class StockLevelBase(BaseModel):
    quantity: int = Field(default=0, ge=0)


class StockLevelCreate(StockLevelBase):
    item_id: uuid.UUID
    store_id: uuid.UUID


class StockLevelUpdate(StockLevelBase):
    pass


class StockLevel(StockLevelBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    item_id: uuid.UUID = Field(
        foreign_key="item.id", nullable=False, ondelete="CASCADE"
    )
    store_id: uuid.UUID = Field(
        foreign_key="store.id", nullable=False, ondelete="CASCADE"
    )

    organization: "Organization" = Relationship()
    created_by: "User" = Relationship()
    item: "Item" = Relationship(back_populates="stock_levels")
    store: "Store" = Relationship(back_populates="stock_levels")


class StockLevelPublic(StockLevelBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    item_id: uuid.UUID
    store_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class StockLevelsPublic(BaseModel):
    data: list[StockLevelPublic]
    count: int
