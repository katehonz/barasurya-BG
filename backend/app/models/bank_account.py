"""
Банкови сметки на организацията.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.bank_transaction import BankTransaction
    from app.models.bank_statement import BankStatement


class BankAccountType(str, Enum):
    """Тип банкова сметка."""
    CURRENT = "current"
    SAVINGS = "savings"
    FOREIGN_CURRENCY = "foreign_currency"


class BankAccountBase(BaseModel):
    """Базов модел за банкова сметка."""
    account_no: str = Field(max_length=50, description="Номер на сметката")
    iban: str = Field(max_length=34, index=True, description="IBAN")
    bic: str | None = Field(default=None, max_length=11, description="BIC/SWIFT код")
    account_type: BankAccountType = Field(default=BankAccountType.CURRENT, description="Тип сметка")
    currency: str = Field(default="BGN", max_length=3, description="Валута")
    is_active: bool = Field(default=True, description="Активна ли е сметката")

    # Данни за банката
    bank_name: str = Field(max_length=255, description="Име на банката")
    bank_code: str | None = Field(default=None, max_length=20, description="Код на банката")
    branch_name: str | None = Field(default=None, max_length=255, description="Клон")

    # Салда
    initial_balance: Decimal = Field(default=Decimal("0.00"), max_digits=18, decimal_places=2, description="Начално салдо")
    current_balance: Decimal = Field(default=Decimal("0.00"), max_digits=18, decimal_places=2, description="Текущо салдо")

    # Допълнителна информация
    notes: str | None = Field(default=None, description="Бележки")


class BankAccountCreate(BankAccountBase):
    """Схема за създаване на банкова сметка."""
    pass


class BankAccountUpdate(BaseModel):
    """Схема за актуализация на банкова сметка."""
    account_no: str | None = None
    iban: str | None = None
    bic: str | None = None
    account_type: BankAccountType | None = None
    currency: str | None = None
    is_active: bool | None = None
    bank_name: str | None = None
    bank_code: str | None = None
    branch_name: str | None = None
    current_balance: Decimal | None = None
    notes: str | None = None


class BankAccount(BankAccountBase, table=True):
    """Банкова сметка."""
    __tablename__ = "bank_account"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    organization: "Organization" = Relationship(back_populates="bank_accounts")
    bank_transactions: list["BankTransaction"] = Relationship(back_populates="bank_account")
    bank_statements: list["BankStatement"] = Relationship(back_populates="bank_account")


class BankAccountPublic(BankAccountBase):
    """Публична схема за банкова сметка."""
    id: uuid.UUID
    organization_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class BankAccountsPublic(BaseModel):
    """Списък банкови сметки."""
    data: list[BankAccountPublic]
    count: int
