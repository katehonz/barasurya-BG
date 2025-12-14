import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.purchase import Purchase
    from app.models.purchase_return_item import PurchaseReturnItem
    from app.models.contraagent import Contraagent
    from app.models.user import User


class PurchaseReturnBase(BaseModel):
    date_return: datetime
    amount: float = Field(default=0, ge=0)
    description: str | None = Field(default=None, max_length=255)


class PurchaseReturnCreate(PurchaseReturnBase):
    pass


class PurchaseReturnUpdate(PurchaseReturnBase):
    date_return: datetime | None = Field(default=0)  # type: ignore
    amount: float | None = Field(default=0, ge=0)  # type: ignore


class PurchaseReturn(PurchaseReturnBase, table=True):
    __tablename__ = "purchase_return"

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
    purchase_id: uuid.UUID = Field(
        foreign_key="purchase.id", nullable=False, ondelete="CASCADE"
    )

    organization: "Organization" = Relationship(back_populates="purchase_returns")
    created_by: "User" = Relationship()
    contraagent: "Contraagent" = Relationship(back_populates="purchase_returns")
    purchase: "Purchase" = Relationship(back_populates="purchase_returns")
    purchase_return_items: list["PurchaseReturnItem"] = Relationship(
        back_populates="purchase_return", cascade_delete=True
    )


class PurchaseReturnPublic(PurchaseReturnBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    contraagent_id: uuid.UUID
    purchase_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class PurchaseReturnsPublic(BaseModel):
    data: list[PurchaseReturnPublic]
    count: int
