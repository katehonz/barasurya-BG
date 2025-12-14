"""
ДДС декларация (VAT Return) според ЗДДС.
Месечна или тримесечна декларация за начислен и приспадащ се ДДС.
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


class VatReturnStatus(str, Enum):
    """Статус на ДДС декларация."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"


class VatReturnBase(BaseModel):
    """Базов модел за ДДС декларация."""
    period_year: int = Field(description="Година на периода")
    period_month: int = Field(ge=1, le=12, description="Месец на периода")
    status: VatReturnStatus = Field(default=VatReturnStatus.DRAFT, description="Статус")

    # Начислен ДДС по продажби
    total_sales_taxable: Decimal | None = Field(default=None, max_digits=18, decimal_places=2, description="Общо данъчна основа продажби")
    total_sales_vat: Decimal | None = Field(default=None, max_digits=18, decimal_places=2, description="Общо ДДС продажби")

    # Приспадащ се ДДС по покупки
    total_purchases_taxable: Decimal | None = Field(default=None, max_digits=18, decimal_places=2, description="Общо данъчна основа покупки")
    total_purchases_vat: Decimal | None = Field(default=None, max_digits=18, decimal_places=2, description="Общо ДДС покупки")
    total_deductible_vat: Decimal | None = Field(default=None, max_digits=18, decimal_places=2, description="Общо приспадащ се ДДС")

    # Резултат
    vat_payable: Decimal | None = Field(default=None, max_digits=18, decimal_places=2, description="ДДС за внасяне")
    vat_refundable: Decimal | None = Field(default=None, max_digits=18, decimal_places=2, description="ДДС за възстановяване")

    # Дати
    submission_date: date | None = Field(default=None, description="Дата на подаване")
    due_date: date | None = Field(default=None, description="Срок за подаване")

    # Забележки
    notes: str | None = Field(default=None, description="Бележки")


class VatReturnCreate(VatReturnBase):
    """Схема за създаване на ДДС декларация."""
    pass


class VatReturnUpdate(BaseModel):
    """Схема за актуализация на ДДС декларация."""
    status: VatReturnStatus | None = None
    total_sales_taxable: Decimal | None = None
    total_sales_vat: Decimal | None = None
    total_purchases_taxable: Decimal | None = None
    total_purchases_vat: Decimal | None = None
    total_deductible_vat: Decimal | None = None
    vat_payable: Decimal | None = None
    vat_refundable: Decimal | None = None
    submission_date: date | None = None
    notes: str | None = None


class VatReturn(VatReturnBase, table=True):
    """ДДС декларация."""
    __tablename__ = "vat_return"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    organization: "Organization" = Relationship(back_populates="vat_returns")


class VatReturnPublic(VatReturnBase):
    """Публична схема за ДДС декларация."""
    id: uuid.UUID
    organization_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class VatReturnsPublic(BaseModel):
    """Списък ДДС декларации."""
    data: list[VatReturnPublic]
    count: int
