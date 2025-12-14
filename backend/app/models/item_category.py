import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.organization import Organization
    from app.models.user import User


class ItemCategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class ItemCategoryCreate(ItemCategoryBase):
    pass


class ItemCategoryUpdate(ItemCategoryBase):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class ItemCategory(ItemCategoryBase, table=True):
    __tablename__ = "item_category"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    organization: "Organization" = Relationship(back_populates="item_categories")
    created_by: "User" = Relationship()
    items: list["Item"] = Relationship(
        back_populates="item_category", cascade_delete=True
    )


class ItemCategoryPublic(ItemCategoryBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class ItemCategoriesPublic(BaseModel):
    data: list[ItemCategoryPublic]
    count: int
