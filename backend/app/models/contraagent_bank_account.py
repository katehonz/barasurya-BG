import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.contraagent import Contraagent


class ContraagentBankAccountBase(BaseModel):
    iban: str = Field(min_length=15, max_length=50)
    bic: str | None = Field(default=None, max_length=20)  # SWIFT/BIC code
    bank_name: str | None = Field(default=None, max_length=255)
    account_number: str | None = Field(default=None, max_length=50)
    currency: str = Field(default="BGN", max_length=3)
    is_primary: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    notes: str | None = Field(default=None, max_length=500)


class ContraagentBankAccountCreate(ContraagentBankAccountBase):
    contraagent_id: uuid.UUID


class ContraagentBankAccountUpdate(BaseModel):
    iban: str | None = Field(default=None, min_length=15, max_length=50)
    bic: str | None = Field(default=None, max_length=20)
    bank_name: str | None = Field(default=None, max_length=255)
    account_number: str | None = Field(default=None, max_length=50)
    currency: str | None = Field(default=None, max_length=3)
    is_primary: bool | None = None
    is_verified: bool | None = None
    notes: str | None = Field(default=None, max_length=500)


class ContraagentBankAccount(ContraagentBankAccountBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    contraagent_id: uuid.UUID = Field(
        foreign_key="contraagent.id", nullable=False, ondelete="CASCADE", index=True
    )

    # Tracking fields for supplier bank accounts from invoices
    first_seen_at: datetime | None = Field(default=None)
    last_seen_at: datetime | None = Field(default=None)
    times_seen: int = Field(default=0)

    # Relationships
    contraagent: "Contraagent" = Relationship(back_populates="bank_accounts")


class ContraagentBankAccountPublic(ContraagentBankAccountBase):
    id: uuid.UUID
    contraagent_id: uuid.UUID
    date_created: datetime
    date_updated: datetime
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    times_seen: int


class ContraagentBankAccountsPublic(BaseModel):
    data: list[ContraagentBankAccountPublic]
    count: int
