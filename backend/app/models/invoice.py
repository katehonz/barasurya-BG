import uuid
import enum
from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING, ForwardRef
from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel
from app.utils import utcnow

from .invoice_line import (
    InvoiceLineCreate,
    InvoiceLineUpdate,
    InvoiceLinePublic,
)

if TYPE_CHECKING:
    from app.models.contraagent import ContraagentPublic
    from app.models.contraagent import Contraagent
    from app.models.account import Account
    from app.models.currency import Currency
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.vat_sales_register import VatSalesRegister
    from .invoice_line import InvoiceLine


class VatDocumentType(str, enum.Enum):
    """Bulgarian VAT document types according to NRA requirements."""

    INVOICE = "01"
    DEBIT_NOTE = "02"
    CREDIT_NOTE = "03"
    PROFORMA_INVOICE = "04"
    INVOICE_FOR_ADVANCE_PAYMENT = "05"
    INVOICE_FOR_FINAL_SETTLEMENT = "06"
    CUSTOMS_DOCUMENT = "07"
    BANK_DOCUMENT = "08"
    FISCAL_RECEIPT = "09"
    DOCUMENT_FOR_INTRACOMMUNITY_SUPPLY = "10"
    DOCUMENT_FOR_INTRACOMMUNITY_ACQUISITION = "11"
    DOCUMENT_FOR_EXPORT = "12"
    DOCUMENT_FOR_IMPORT = "13"
    DOCUMENT_FOR_SUPPLY_OF_SERVICES_ABROAD = "14"
    DOCUMENT_FOR_ACQUISITION_OF_SERVICES_ABROAD = "15"
    VAT_PROTOCOL = "96"


class VatExemptionReason(str, enum.Enum):
    """VAT exemption reasons for Bulgarian documents."""

    INTRACOMMUNITY_SUPPLY = "01"
    EXPORT = "02"
    SERVICES_ABROAD = "03"
    INVESTMENT = "04"
    FINANCIAL_SERVICES = "05"
    EDUCATION = "06"
    HEALTHCARE = "07"
    INSURANCE = "08"
    GAMING = "09"
    POSTAL_SERVICES = "10"
    TELECOMMUNICATIONS = "11"
    BROADCASTING = "12"
    ELECTRONIC_SERVICES = "13"
    REAL_ESTATE = "14"
    SOCIAL_HOUSING = "15"
    AGRICULTURAL = "16"
    FISHING = "17"
    TOURISM = "18"
    SPORT = "19"
    CULTURE = "20"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceBase(BaseModel):
    issue_date: date
    due_date: Optional[date] = None
    tax_event_date: Optional[date] = None

    billing_name: str = Field(max_length=255)
    billing_address: Optional[str] = Field(default=None, max_length=255)
    billing_vat_number: Optional[str] = Field(default=None, max_length=50)
    billing_company_id: Optional[str] = Field(default=None, max_length=50)

    subtotal: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    tax_amount: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    total_amount: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    paid_amount: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    currency_code: str = Field(
        default="BGN", max_length=3, description="Invoice currency code (ISO 4217)"
    )
    currency_id: uuid.UUID | None = Field(
        default=None, foreign_key="currencies.id", description="Currency reference"
    )
    exchange_rate: Decimal | None = Field(
        default=None,
        max_digits=15,
        decimal_places=6,
        description="Exchange rate to base currency",
    )
    is_multicurrency: bool = Field(
        default=False, description="Whether this is a multi-currency invoice"
    )

    payment_method: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = None
    payment_terms: Optional[str] = None
    reference: Optional[str] = None

    vat_document_type: str = Field(default=VatDocumentType.INVOICE, max_length=2)
    vat_reason: Optional[str] = None
    oss_country: Optional[str] = Field(default=None, max_length=2)
    oss_vat_rate: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2
    )


class Invoice(InvoiceBase, table=True):
    __tablename__ = "invoices"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    invoice_no: str = Field(max_length=50, index=True, nullable=False)
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT, nullable=False)

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    organization: "Organization" = Relationship(back_populates="invoices")
    created_by: "User" = Relationship()

    contact_id: uuid.UUID = Field(foreign_key="contraagent.id", nullable=False)
    contact: "Contraagent" = Relationship()

    bank_account_id: Optional[uuid.UUID] = Field(default=None, foreign_key="account.id")
    bank_account: Optional["Account"] = Relationship()

    parent_invoice_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="invoices.id"
    )
    parent_invoice: Optional["Invoice"] = Relationship(
        back_populates="child_invoices",
        sa_relationship_kwargs=dict(remote_side="Invoice.id"),
    )
    child_invoices: List["Invoice"] = Relationship(back_populates="parent_invoice")

    invoice_lines: List["InvoiceLine"] = Relationship(
        back_populates="invoice",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    currency: Optional["Currency"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Invoice.currency_id]"}
    )
    # TODO: Re-enable when invoice table migration is added
    # vat_sales_register_entry: Optional["VatSalesRegister"] = Relationship(back_populates="invoice")


class InvoiceCreate(InvoiceBase):
    contact_id: uuid.UUID
    invoice_no: str
    invoice_lines: List[InvoiceLineCreate]


class InvoiceUpdate(SQLModel):
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    billing_name: Optional[str] = None
    # ... other fields
    invoice_lines: Optional[List[InvoiceLineUpdate]] = None


class InvoicePublic(InvoiceBase):
    id: uuid.UUID
    invoice_no: str
    status: InvoiceStatus
    contact: "ContraagentPublic"
    invoice_lines: List[InvoiceLinePublic]


class InvoicesPublic(BaseModel):
    data: List[InvoicePublic]
    count: int
