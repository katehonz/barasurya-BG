"""
Банкови извлечения.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.bank_account import BankAccount


class BankStatementStatus(str, Enum):
    """Статус на банково извлечение."""
    DRAFT = "draft"
    IMPORTED = "imported"
    RECONCILED = "reconciled"
    ARCHIVED = "archived"


class BankStatementBase(BaseModel):
    """Базов модел за банково извлечение."""
    statement_no: str | None = Field(default=None, max_length=50, description="Номер на извлечението")
    status: BankStatementStatus = Field(default=BankStatementStatus.DRAFT, description="Статус")
    statement_date: date = Field(description="Дата на извлечението")
    from_date: date = Field(description="Начална дата на периода")
    to_date: date = Field(description="Крайна дата на периода")

    # Салда
    opening_balance: Decimal = Field(default=Decimal("0.00"), max_digits=18, decimal_places=2, description="Начално салдо")
    closing_balance: Decimal = Field(default=Decimal("0.00"), max_digits=18, decimal_places=2, description="Крайно салдо")
    total_debits: Decimal = Field(default=Decimal("0.00"), max_digits=18, decimal_places=2, description="Общо дебит")
    total_credits: Decimal = Field(default=Decimal("0.00"), max_digits=18, decimal_places=2, description="Общо кредит")

    # Метаданни за импорт
    file_name: str | None = Field(default=None, max_length=255, description="Име на файла")
    file_format: str | None = Field(default=None, max_length=50, description="Формат на файла")
    import_date: datetime | None = Field(default=None, description="Дата на импорт")

    # Допълнителна информация
    notes: str | None = Field(default=None, description="Бележки")


class BankStatementCreate(BankStatementBase):
    """Схема за създаване на банково извлечение."""
    bank_account_id: uuid.UUID


class BankStatementUpdate(BaseModel):
    """Схема за актуализация на банково извлечение."""
    statement_no: str | None = None
    status: BankStatementStatus | None = None
    opening_balance: Decimal | None = None
    closing_balance: Decimal | None = None
    total_debits: Decimal | None = None
    total_credits: Decimal | None = None
    notes: str | None = None


class BankStatement(BankStatementBase, table=True):
    """Банково извлечение."""
    __tablename__ = "bank_statement"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)
    bank_account_id: uuid.UUID = Field(foreign_key="bank_account.id", index=True)

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    organization: "Organization" = Relationship(back_populates="bank_statements")
    bank_account: "BankAccount" = Relationship(back_populates="bank_statements")


class BankStatementPublic(BankStatementBase):
    """Публична схема за банково извлечение."""
    id: uuid.UUID
    organization_id: uuid.UUID
    bank_account_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class BankStatementsPublic(BaseModel):
    """Списък банкови извлечения."""
    data: list[BankStatementPublic]
    count: int
