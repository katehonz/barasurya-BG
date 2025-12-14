"""
Дневник продажби (Sales Register) според ЗДДС.

Всяка регистрирана по ЗДДС компания трябва да води дневник на продажбите,
в който се вписват всички издадени данъчни документи.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.invoice import Invoice


class VatSalesRegisterBase(BaseModel):
    """Базов модел за дневник продажби."""
    # Период
    period_year: int = Field(description="Година на периода")
    period_month: int = Field(ge=1, le=12, description="Месец на периода")

    # Данни за документа
    document_date: date = Field(description="Дата на документа")
    tax_event_date: date = Field(description="Дата на данъчното събитие")
    document_type: str = Field(max_length=20, description="Тип документ")
    document_number: str = Field(max_length=50, description="Номер на документа")
    sales_operation: str | None = Field(default=None, max_length=50, description="Операция по продажба")

    # Данни за контрагент
    recipient_name: str = Field(max_length=255, description="Име на получател")
    recipient_vat_number: str | None = Field(default=None, max_length=20, description="ДДС номер на получател")
    recipient_country: str = Field(default="BG", max_length=2, description="Държава на получател")
    recipient_eik: str | None = Field(default=None, max_length=20, description="ЕИК на получател")
    recipient_city: str | None = Field(default=None, max_length=100, description="Град на получател")

    # Финансови данни
    taxable_base: Decimal = Field(max_digits=18, decimal_places=2, description="Данъчна основа")
    vat_rate: Decimal = Field(max_digits=5, decimal_places=2, description="Ставка ДДС")
    vat_amount: Decimal = Field(max_digits=18, decimal_places=2, description="Сума ДДС")
    total_amount: Decimal = Field(max_digits=18, decimal_places=2, description="Обща сума")

    # Detailed VAT operation codes
    vat_operation_code: str | None = Field(default=None, max_length=20, description="Код на ДДС операция")
    column_code: str | None = Field(default=None, max_length=20, description="Код на колона")
    vies_indicator: str | None = Field(default=None, max_length=5, description="VIES индикатор (к3, к4, к5)")
    reverse_charge_subcode: str | None = Field(default=None, max_length=5, description="Подкод за обратно начисляване")
    is_triangular_operation: bool = Field(default=False, description="Триъгълна операция")
    is_art_21_service: bool = Field(default=False, description="Услуга по чл. 21")

    # Забележки
    notes: str | None = Field(default=None, description="Бележки")


class VatSalesRegisterCreate(VatSalesRegisterBase):
    """Схема за създаване на запис в дневник продажби."""
    invoice_id: uuid.UUID | None = None


class VatSalesRegisterUpdate(BaseModel):
    """Схема за актуализация на запис в дневник продажби."""
    document_date: date | None = None
    tax_event_date: date | None = None
    recipient_name: str | None = None
    recipient_vat_number: str | None = None
    taxable_base: Decimal | None = None
    vat_rate: Decimal | None = None
    vat_amount: Decimal | None = None
    total_amount: Decimal | None = None
    vat_operation_code: str | None = None
    notes: str | None = None


class VatSalesRegister(VatSalesRegisterBase, table=True):
    """Запис в дневник продажби."""
    __tablename__ = "vat_sales_register"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)
    invoice_id: uuid.UUID | None = Field(default=None, foreign_key="invoices.id", index=True)

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    organization: "Organization" = Relationship(back_populates="vat_sales_registers")
    invoice: "Invoice" = Relationship(back_populates="vat_sales_register_entry")


class VatSalesRegisterPublic(VatSalesRegisterBase):
    """Публична схема за дневник продажби."""
    id: uuid.UUID
    organization_id: uuid.UUID
    # TODO: Re-enable when invoice table migration is added
    # invoice_id: uuid.UUID | None = None
    date_created: datetime
    date_updated: datetime


class VatSalesRegistersPublic(BaseModel):
    """Списък записи от дневник продажби."""
    data: list[VatSalesRegisterPublic]
    count: int
