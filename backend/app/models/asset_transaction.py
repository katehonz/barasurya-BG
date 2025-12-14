
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.asset import Asset
    from app.models.journal_entry import JournalEntry
    from app.models.organization import Organization
    from app.models.supplier import Supplier
    from app.models.user import User


class AssetTransactionBase(SQLModel):
    transaction_type: str
    transaction_date: date
    description: str | None = Field(default=None)
    transaction_amount: float
    acquisition_cost_change: float | None = Field(default=None)
    book_value_after: float | None = Field(default=None)
    saft_transaction_id: str | None = Field(default=None)
    year: int
    month: int


class AssetTransactionCreate(AssetTransactionBase):
    asset_id: uuid.UUID
    supplier_customer_id: uuid.UUID | None = None
    journal_entry_id: uuid.UUID | None = None


class AssetTransactionUpdate(AssetTransactionBase):
    pass


class AssetTransaction(AssetTransactionBase, table=True):
    __tablename__ = "asset_transaction"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    asset_id: uuid.UUID = Field(
        foreign_key="asset.id", nullable=False, ondelete="CASCADE"
    )
    supplier_customer_id: uuid.UUID | None = Field(
        default=None, foreign_key="supplier.id", ondelete="SET NULL"
    )
    journal_entry_id: uuid.UUID | None = Field(
        default=None, foreign_key="journal_entry.id", ondelete="SET NULL"
    )

    organization: "Organization" = Relationship()
    created_by: "User" = Relationship()
    asset: "Asset" = Relationship(back_populates="transactions")
    supplier_customer: Optional["Supplier"] = Relationship()
    journal_entry: Optional["JournalEntry"] = Relationship()


class AssetTransactionPublic(AssetTransactionBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    asset_id: uuid.UUID
    date_created: datetime


class AssetTransactionsPublic(SQLModel):
    data: list[AssetTransactionPublic]
    count: int
