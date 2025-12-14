"""
Запис за банков импорт.

Поддържа:
- Автоматичен импорт от Salt Edge (saltedge_auto)
- Ръчен импорт от Salt Edge (saltedge_manual)
- Импорт от файл (file_upload)
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.bank_profile import BankProfile
    from app.models.bank_transaction import BankTransaction
    from app.models.user import User


class BankImportType(str, Enum):
    """Тип импорт."""
    SALTEDGE_AUTO = "saltedge_auto"
    SALTEDGE_MANUAL = "saltedge_manual"
    FILE_UPLOAD = "file_upload"


class BankImportStatus(str, Enum):
    """Статус на импорт."""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class BankImportBase(BaseModel):
    """Базов модел за банков импорт."""
    import_type: BankImportType = Field(description="Тип импорт")
    file_name: str | None = Field(default=None, max_length=255, description="Име на файла")
    import_format: str | None = Field(default=None, max_length=50, description="Формат на импорта")
    imported_at: datetime = Field(description="Дата/час на импорт")
    transactions_count: int = Field(default=0, description="Брой транзакции")
    total_credit: Decimal = Field(default=Decimal("0.00"), max_digits=18, decimal_places=2, description="Общо кредит")
    total_debit: Decimal = Field(default=Decimal("0.00"), max_digits=18, decimal_places=2, description="Общо дебит")
    created_journal_entries: int = Field(default=0, description="Създадени счетоводни записи")
    status: BankImportStatus = Field(default=BankImportStatus.IN_PROGRESS, description="Статус")
    error_message: str | None = Field(default=None, description="Съобщение за грешка")
    period_from: date | None = Field(default=None, description="Начална дата на периода")
    period_to: date | None = Field(default=None, description="Крайна дата на периода")
    saltedge_attempt_id: str | None = Field(default=None, max_length=100, description="Salt Edge attempt ID")


class BankImportCreate(BankImportBase):
    """Схема за създаване на банков импорт."""
    bank_profile_id: uuid.UUID


class BankImportUpdate(BaseModel):
    """Схема за актуализация на банков импорт."""
    status: BankImportStatus | None = None
    transactions_count: int | None = None
    total_credit: Decimal | None = None
    total_debit: Decimal | None = None
    created_journal_entries: int | None = None
    error_message: str | None = None
    journal_entry_ids: list[uuid.UUID] | None = None


class BankImport(BankImportBase, table=True):
    """Банков импорт."""
    __tablename__ = "bank_import"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)
    bank_profile_id: uuid.UUID = Field(foreign_key="bank_profile.id", index=True)
    created_by_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    # Journal entry IDs (stored as array)
    journal_entry_ids: list[uuid.UUID] | None = Field(
        default=None,
        sa_column=Column(ARRAY(PG_UUID(as_uuid=True)))
    )

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    organization: "Organization" = Relationship(back_populates="bank_imports")
    bank_profile: "BankProfile" = Relationship(back_populates="bank_imports")
    created_by: "User" = Relationship()
    bank_transactions: list["BankTransaction"] = Relationship(back_populates="bank_import")


class BankImportPublic(BankImportBase):
    """Публична схема за банков импорт."""
    id: uuid.UUID
    organization_id: uuid.UUID
    bank_profile_id: uuid.UUID
    created_by_id: uuid.UUID | None = None
    date_created: datetime
    date_updated: datetime


class BankImportsPublic(BaseModel):
    """Списък банкови импорти."""
    data: list[BankImportPublic]
    count: int
