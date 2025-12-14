
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.journal_entry import JournalEntry
    from app.models.organization import Organization
    from app.models.user import User


class EntryLineBase(SQLModel):
    debit: float = Field(default=0, ge=0)
    credit: float = Field(default=0, ge=0)
    description: str | None = Field(default=None, max_length=255)


class EntryLineCreate(EntryLineBase):
    account_id: uuid.UUID


class EntryLineUpdate(EntryLineBase):
    pass


class EntryLine(EntryLineBase, table=True):
    __tablename__ = "entry_line"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    journal_entry_id: uuid.UUID = Field(
        foreign_key="journal_entry.id", nullable=False, ondelete="CASCADE"
    )
    account_id: uuid.UUID = Field(
        foreign_key="account.id", nullable=False, ondelete="CASCADE"
    )

    organization: "Organization" = Relationship()
    created_by: "User" = Relationship()
    journal_entry: "JournalEntry" = Relationship(back_populates="lines")
    account: "Account" = Relationship()


class EntryLinePublic(EntryLineBase):
    id: uuid.UUID
    date_created: datetime
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    journal_entry_id: uuid.UUID
    account_id: uuid.UUID


class EntryLinesPublic(SQLModel):
    data: list[EntryLinePublic]
    count: int

