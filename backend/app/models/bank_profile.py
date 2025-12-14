"""
Конфигурация на банкова сметка.

Поддържа:
- Ръчен импорт на файлове (MT940, CAMT053, CSV, XML)
- Автоматична синхронизация през Salt Edge API
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.account import Account
    from app.models.user import User
    from app.models.bank_import import BankImport
    from app.models.bank_transaction import BankTransaction


class BankImportFormat(str, Enum):
    """Формат за импорт на банкови извлечения."""
    MT940 = "mt940"
    CAMT053_WISE = "camt053_wise"
    CAMT053_REVOLUT = "camt053_revolut"
    CAMT053_PAYSERA = "camt053_paysera"
    CCB_CSV = "ccb_csv"
    POSTBANK_XML = "postbank_xml"
    OBB_XML = "obb_xml"


class BankProfileBase(BaseModel):
    """Базов модел за банков профил."""
    name: str = Field(max_length=255, description="Име на профила")
    iban: str | None = Field(default=None, max_length=34, index=True, description="IBAN")
    bic: str | None = Field(default=None, max_length=11, description="BIC/SWIFT код")
    bank_name: str | None = Field(default=None, max_length=255, description="Име на банката")
    currency_code: str = Field(default="BGN", max_length=3, description="Валута")
    import_format: BankImportFormat | None = Field(default=None, description="Формат за импорт")
    is_active: bool = Field(default=True, description="Активен ли е профила")

    # Salt Edge integration
    saltedge_connection_id: str | None = Field(default=None, max_length=100, description="Salt Edge connection ID")
    saltedge_account_id: str | None = Field(default=None, max_length=100, description="Salt Edge account ID")
    auto_sync_enabled: bool = Field(default=False, description="Автоматична синхронизация")
    last_synced_at: datetime | None = Field(default=None, description="Последна синхронизация")


class BankProfileCreate(BankProfileBase):
    """Схема за създаване на банков профил."""
    bank_account_id: uuid.UUID
    buffer_account_id: uuid.UUID
    settings: dict[str, Any] | None = None


class BankProfileUpdate(BaseModel):
    """Схема за актуализация на банков профил."""
    name: str | None = None
    iban: str | None = None
    bic: str | None = None
    bank_name: str | None = None
    currency_code: str | None = None
    import_format: BankImportFormat | None = None
    is_active: bool | None = None
    bank_account_id: uuid.UUID | None = None
    buffer_account_id: uuid.UUID | None = None
    saltedge_connection_id: str | None = None
    saltedge_account_id: str | None = None
    auto_sync_enabled: bool | None = None
    settings: dict[str, Any] | None = None


class BankProfile(BankProfileBase, table=True):
    """Банков профил."""
    __tablename__ = "bank_profile"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)
    bank_account_id: uuid.UUID = Field(foreign_key="account.id", description="Счетоводна сметка за банката")
    buffer_account_id: uuid.UUID = Field(foreign_key="account.id", description="Буферна сметка")
    created_by_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")

    # Settings (JSON)
    settings: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    organization: "Organization" = Relationship(back_populates="bank_profiles")
    bank_account: "Account" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BankProfile.bank_account_id]"}
    )
    buffer_account: "Account" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[BankProfile.buffer_account_id]"}
    )
    created_by: "User" = Relationship()
    bank_imports: list["BankImport"] = Relationship(back_populates="bank_profile")
    bank_transactions: list["BankTransaction"] = Relationship(back_populates="bank_profile")


class BankProfilePublic(BankProfileBase):
    """Публична схема за банков профил."""
    id: uuid.UUID
    organization_id: uuid.UUID
    bank_account_id: uuid.UUID
    buffer_account_id: uuid.UUID
    created_by_id: uuid.UUID | None = None
    date_created: datetime
    date_updated: datetime


class BankProfilesPublic(BaseModel):
    """Списък банкови профили."""
    data: list[BankProfilePublic]
    count: int
