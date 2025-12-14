import uuid
from datetime import date
from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel
import enum


class DeductibleCreditType(str, enum.Enum):
    FULL = "full"
    PARTIAL = "partial"
    NONE = "none"


class VatPurchaseRegisterBase(BaseModel):
    document_type: str = Field(max_length=2)
    document_number: str = Field(max_length=20)
    document_date: date

    supplier_vat_number: str | None = Field(default=None, max_length=15)
    supplier_name: str = Field(max_length=70)

    taxable_base: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    vat_amount: Decimal = Field(default=0, max_digits=15, decimal_places=2)


class VatPurchaseRegister(VatPurchaseRegisterBase, table=True):
    __tablename__ = "vat_purchase_registers"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, index=True
    )
    period_year: int = Field(nullable=False, index=True)
    period_month: int = Field(nullable=False, index=True)


class VatPurchaseRegisterCreate(VatPurchaseRegisterBase):
    pass


class VatPurchaseRegisterUpdate(SQLModel):
    pass


class VatPurchaseRegisterPublic(VatPurchaseRegisterBase):


    id: uuid.UUID





class VatPurchaseRegistersPublic(BaseModel):


    data: list[VatPurchaseRegisterPublic]


    count: int

