
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.bank_transaction import BankTransaction
    from app.models.entry_line import EntryLine
    from app.models.organization import Organization
    from app.models.user import User


class JournalEntryBase(SQLModel):
    date: date
    description: str
    is_posted: bool = Field(default=False)
    document_date: date | None = Field(default=None)
    document_reference: str | None = Field(default=None)


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(JournalEntryBase):
    pass


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

    organization: "Organization" = Relationship(back_populates="journal_entries")
    created_by: "User" = Relationship()
    lines: List["EntryLine"] = Relationship(back_populates="journal_entry")
    bank_transactions: List["BankTransaction"] = Relationship(back_populates="journal_entry")


class JournalEntryPublic(JournalEntryBase):
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime
    organization_id: uuid.UUID
    created_by_id: uuid.UUID


class JournalEntriesPublic(SQLModel):
    data: List[JournalEntryPublic]
    count: int
