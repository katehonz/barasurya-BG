"""
Дневник покупки (Purchase Register) според ЗДДС.

Всяка регистрирана по ЗДДС компания трябва да води дневник на покупките,
в който се вписват всички получени данъчни документи от доставчици.
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


class DeductibleCreditType(str, Enum):
    """Тип данъчен кредит."""
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"
    NOT_APPLICABLE = "not_applicable"


class VatPurchaseRegisterBase(BaseModel):
    """Базов модел за дневник покупки."""
    # Период
    period_year: int = Field(description="Година на периода")
    period_month: int = Field(ge=1, le=12, description="Месец на периода")

    # Връзка към документ (полиморфна)
    document_id: uuid.UUID | None = Field(default=None, description="ID на документа")
    document_type_table: str | None = Field(default=None, max_length=50, description="Таблица на документа")

    # Данни за документа
    document_date: date = Field(description="Дата на документа")
    tax_event_date: date = Field(description="Дата на данъчното събитие")
    document_type: str = Field(max_length=20, description="Тип документ")
    document_number: str = Field(max_length=50, description="Номер на документа")
    purchase_operation: str | None = Field(default=None, max_length=50, description="Операция по покупка")

    # Данни за контрагент (доставчик)
    supplier_name: str = Field(max_length=255, description="Име на доставчик")
    supplier_vat_number: str | None = Field(default=None, max_length=20, description="ДДС номер на доставчик")
    supplier_country: str = Field(default="BG", max_length=2, description="Държава на доставчик")
    supplier_eik: str | None = Field(default=None, max_length=20, description="ЕИК на доставчик")
    supplier_city: str | None = Field(default=None, max_length=100, description="Град на доставчик")

    # Финансови данни
    taxable_base: Decimal = Field(max_digits=18, decimal_places=2, description="Данъчна основа")
    vat_rate: Decimal = Field(max_digits=5, decimal_places=2, description="Ставка ДДС")
    vat_amount: Decimal = Field(max_digits=18, decimal_places=2, description="Сума ДДС")
    total_amount: Decimal = Field(max_digits=18, decimal_places=2, description="Обща сума")

    # За приспадане на ДДС
    is_deductible: bool = Field(default=True, description="Приспада ли се ДДС")
    deductible_vat_amount: Decimal | None = Field(default=None, max_digits=18, decimal_places=2, description="Сума приспадащ се ДДС")

    # Detailed VAT operation codes
    vat_operation_code: str | None = Field(default=None, max_length=20, description="Код на ДДС операция")
    column_code: str | None = Field(default=None, max_length=20, description="Код на колона")
    deductible_credit_type: DeductibleCreditType = Field(default=DeductibleCreditType.FULL, description="Тип данъчен кредит")
    vies_indicator: str | None = Field(default=None, max_length=5, description="VIES индикатор")
    reverse_charge_subcode: str | None = Field(default=None, max_length=5, description="Подкод за обратно начисляване")
    is_triangular_operation: bool = Field(default=False, description="Триъгълна операция")
    is_art_21_service: bool = Field(default=False, description="Услуга по чл. 21")

    # Забележки
    notes: str | None = Field(default=None, description="Бележки")


class VatPurchaseRegisterCreate(VatPurchaseRegisterBase):
    """Схема за създаване на запис в дневник покупки."""
    pass


class VatPurchaseRegisterUpdate(BaseModel):
    """Схема за актуализация на запис в дневник покупки."""
    document_date: date | None = None
    tax_event_date: date | None = None
    supplier_name: str | None = None
    supplier_vat_number: str | None = None
    taxable_base: Decimal | None = None
    vat_rate: Decimal | None = None
    vat_amount: Decimal | None = None
    total_amount: Decimal | None = None
    is_deductible: bool | None = None
    deductible_vat_amount: Decimal | None = None
    vat_operation_code: str | None = None
    deductible_credit_type: DeductibleCreditType | None = None
    notes: str | None = None


class VatPurchaseRegister(VatPurchaseRegisterBase, table=True):
    """Запис в дневник покупки."""
    __tablename__ = "vat_purchase_register"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    organization: "Organization" = Relationship(back_populates="vat_purchase_registers")


class VatPurchaseRegisterPublic(VatPurchaseRegisterBase):
    """Публична схема за дневник покупки."""
    id: uuid.UUID
    organization_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class VatPurchaseRegistersPublic(BaseModel):
    """Списък записи от дневник покупки."""
    data: list[VatPurchaseRegisterPublic]
    count: int
