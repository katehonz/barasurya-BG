
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column
from sqlalchemy.types import JSON
from sqlmodel import Field, Relationship, SQLModel

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.asset_depreciation_schedule import AssetDepreciationSchedule
    from app.models.asset_transaction import AssetTransaction
    from app.models.journal_entry import JournalEntry
    from app.models.organization import Organization
    from app.models.supplier import Supplier
    from app.models.user import User


class AssetBase(BaseModel):
    code: str = Field(index=True)
    name: str
    category: str | None = Field(default=None)
    inventory_number: str | None = Field(default=None, index=True)
    serial_number: str | None = Field(default=None)
    location: str | None = Field(default=None)
    responsible_person: str | None = Field(default=None)
    tax_category: str | None = Field(default=None)
    tax_depreciation_rate: float | None = Field(default=None)
    accounting_depreciation_rate: float | None = Field(default=None)
    acquisition_date: date
    acquisition_cost: float
    startup_date: date | None = Field(default=None)
    purchase_order_date: date | None = Field(default=None)
    invoice_number: str | None = Field(default=None)
    invoice_date: date | None = Field(default=None)
    salvage_value: float = Field(default=0)
    useful_life_months: int
    depreciation_method: str
    status: str = Field(default="active")
    residual_value: float = Field(default=0)
    disposal_date: date | None = Field(default=None)
    disposal_reason: str | None = Field(default=None)
    disposal_value: float | None = Field(default=None)
    notes: str | None = Field(default=None)
    attachments: dict | None = Field(default=None)
    metadata: dict | None = Field(default=None)
    month_value_change: int | None = Field(default=None)
    month_suspension_resumption: int | None = Field(default=None)
    month_writeoff_accounting: int | None = Field(default=None)
    month_writeoff_tax: int | None = Field(default=None)
    depreciation_months_current_year: int | None = Field(default=None)
    acquisition_cost_begin_year: float | None = Field(default=None)
    book_value_begin_year: float | None = Field(default=None)
    accumulated_depreciation_begin_year: float | None = Field(default=None)


class AssetCreate(AssetBase):
    supplier_id: uuid.UUID | None = None
    accounting_account_id: uuid.UUID | None = None
    expense_account_id: uuid.UUID | None = None
    accumulated_depreciation_account_id: uuid.UUID | None = None
    disposal_journal_entry_id: uuid.UUID | None = None


class AssetUpdate(AssetBase):
    pass


class Asset(AssetBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    supplier_id: uuid.UUID | None = Field(
        default=None, foreign_key="supplier.id", ondelete="SET NULL"
    )
    accounting_account_id: uuid.UUID | None = Field(
        default=None, foreign_key="account.id", ondelete="SET NULL"
    )
    expense_account_id: uuid.UUID | None = Field(
        default=None, foreign_key="account.id", ondelete="SET NULL"
    )
    accumulated_depreciation_account_id: uuid.UUID | None = Field(
        default=None, foreign_key="account.id", ondelete="SET NULL"
    )
    disposal_journal_entry_id: uuid.UUID | None = Field(
        default=None, foreign_key="journal_entry.id", ondelete="SET NULL"
    )

    organization: "Organization" = Relationship()
    created_by: "User" = Relationship()
    supplier: Optional["Supplier"] = Relationship()
    accounting_account: Optional["Account"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="[Asset.accounting_account_id]")
    )
    expense_account: Optional["Account"] = Relationship(
        sa_relationship_kwargs=dict(foreign_keys="[Asset.expense_account_id]")
    )
    accumulated_depreciation_account: Optional["Account"] = Relationship(
        sa_relationship_kwargs=dict(
            foreign_keys="[Asset.accumulated_depreciation_account_id]"
        )
    )
    disposal_journal_entry: Optional["JournalEntry"] = Relationship()
    depreciation_schedule: List["AssetDepreciationSchedule"] = Relationship(
        back_populates="asset"
    )
    transactions: List["AssetTransaction"] = Relationship(back_populates="asset")


class AssetPublic(AssetBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class AssetsPublic(SQLModel):
    data: List[AssetPublic]
    count: int
