"""
Банкова транзакция (временно хранилище преди създаване на дневен запис).
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.bank_account import BankAccount
    from app.models.bank_import import BankImport
    from app.models.bank_profile import BankProfile
    from app.models.organization import Organization
    from app.models.journal_entry import JournalEntry


class BankTransactionBase(BaseModel):
    """Базов модел за банкова транзакция."""
    booking_date: date = Field(description="Дата на осчетоводяване")
    value_date: date | None = Field(default=None, description="Вальор")
    amount: Decimal = Field(max_digits=18, decimal_places=2, description="Сума")
    currency: str = Field(default="BGN", max_length=3, description="Валута")
    is_credit: bool = Field(description="Кредитна транзакция (приход)")

    # Description & references
    description: str | None = Field(default=None, description="Описание")
    reference: str | None = Field(default=None, max_length=255, description="Референция")
    transaction_id: str | None = Field(default=None, max_length=255, description="Уникален ID на транзакцията")

    # Counterpart info
    counterpart_name: str | None = Field(default=None, max_length=255, description="Име на контрагент")
    counterpart_iban: str | None = Field(default=None, max_length=34, description="IBAN на контрагент")
    counterpart_bic: str | None = Field(default=None, max_length=11, description="BIC на контрагент")

    # Processing
    is_processed: bool = Field(default=False, description="Обработена ли е")
    processed_at: datetime | None = Field(default=None, description="Дата на обработка")


class BankTransactionCreate(BankTransactionBase):
    """Схема за създаване на банкова транзакция."""
    bank_account_id: uuid.UUID
    bank_import_id: uuid.UUID | None = None
    bank_profile_id: uuid.UUID | None = None
    metadata_json: dict[str, Any] | None = None


class BankTransactionUpdate(BaseModel):
    """Схема за актуализация на банкова транзакция."""
    description: str | None = None
    reference: str | None = None
    counterpart_name: str | None = None
    counterpart_iban: str | None = None
    is_processed: bool | None = None
    journal_entry_id: uuid.UUID | None = None
    metadata_json: dict[str, Any] | None = None


class BankTransaction(BankTransactionBase, table=True):
    """Банкова транзакция."""
    __tablename__ = "bank_transaction"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)
    bank_account_id: uuid.UUID = Field(foreign_key="bank_account.id", index=True)
    bank_import_id: uuid.UUID | None = Field(default=None, foreign_key="bank_import.id", index=True)
    bank_profile_id: uuid.UUID | None = Field(default=None, foreign_key="bank_profile.id", index=True)
    journal_entry_id: uuid.UUID | None = Field(default=None, foreign_key="journal_entry.id", index=True)

    # Metadata
    metadata_json: dict[str, Any] | None = Field(default=None, sa_column=Column("metadata", JSON))

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    organization: "Organization" = Relationship(back_populates="bank_transactions")
    bank_account: "BankAccount" = Relationship(back_populates="bank_transactions")
    bank_import: "BankImport" = Relationship(back_populates="bank_transactions")
    bank_profile: "BankProfile" = Relationship(back_populates="bank_transactions")
    journal_entry: "JournalEntry" = Relationship(back_populates="bank_transactions")


class BankTransactionPublic(BankTransactionBase):
    """Публична схема за банкова транзакция."""
    id: uuid.UUID
    organization_id: uuid.UUID
    bank_account_id: uuid.UUID
    bank_import_id: uuid.UUID | None = None
    bank_profile_id: uuid.UUID | None = None
    journal_entry_id: uuid.UUID | None = None
    date_created: datetime
    date_updated: datetime


class BankTransactionsPublic(BaseModel):
    """Списък банкови транзакции."""
    data: list[BankTransactionPublic]
    count: int
