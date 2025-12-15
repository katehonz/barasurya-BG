import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.bank_transaction import BankTransaction
    from app.models.entry_line import EntryLine
    from app.models.organization import Organization
    from app.models.user import User


class JournalEntryBase(SQLModel):
    entry_date: date = Field(nullable=False)
    description: str | None = Field(default=None, max_length=500)
    currency_code: str = Field(default="BGN", max_length=3)
    exchange_rate: float | None = Field(default=1.0)
    reference: str | None = Field(default=None, max_length=100)


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(SQLModel):
    entry_date: date | None = None
    description: str | None = None
    currency_code: str | None = None
    exchange_rate: float | None = None
    reference: str | None = None


class JournalEntry(JournalEntryBase, table=True):
    __tablename__ = "journal_entry"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    organization: "Organization" = Relationship()
    created_by: "User" = Relationship()
    lines: list["EntryLine"] = Relationship(back_populates="journal_entry")
    bank_transactions: list["BankTransaction"] = Relationship(back_populates="journal_entry")


class JournalEntryPublic(JournalEntryBase):
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime
    organization_id: uuid.UUID
    created_by_id: uuid.UUID


class JournalEntriesPublic(SQLModel):
    data: list[JournalEntryPublic]
    count: int
