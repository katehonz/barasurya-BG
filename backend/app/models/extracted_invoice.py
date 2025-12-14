import uuid
import enum
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING, Dict, Any
from decimal import Decimal

from sqlmodel import Field, Relationship, JSON, Column

from app.models.base import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from .document_upload import DocumentUpload
    from .invoice import Invoice
    from .purchase import Purchase


class ExtractedInvoiceStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED = "converted"


class ExtractedInvoiceType(str, enum.Enum):
    SALES = "sales"
    PURCHASE = "purchase"


class ExtractedInvoiceBase(BaseModel):
    invoice_type: ExtractedInvoiceType
    status: ExtractedInvoiceStatus = Field(default=ExtractedInvoiceStatus.PENDING_REVIEW)
    confidence_score: Optional[Decimal] = Field(default=None, max_digits=5, decimal_places=4)

    # Extracted invoice fields
    invoice_number: Optional[str] = Field(default=None, max_length=255)
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None

    # Parties
    vendor_name: Optional[str] = Field(default=None, max_length=255)
    vendor_address: Optional[str] = None
    vendor_vat_number: Optional[str] = Field(default=None, max_length=50)
    customer_name: Optional[str] = Field(default=None, max_length=255)
    customer_address: Optional[str] = None
    customer_vat_number: Optional[str] = Field(default=None, max_length=50)

    # Financial
    subtotal: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    tax_amount: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    total_amount: Optional[Decimal] = Field(default=None, max_digits=15, decimal_places=2)
    currency: str = Field(default="BGN", max_length=3)

    # Data
    line_items: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    raw_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    # Approval
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    # Conversion
    converted_invoice_id: Optional[uuid.UUID] = None
    converted_invoice_type: Optional[str] = None


class ExtractedInvoice(ExtractedInvoiceBase, table=True):
    __tablename__ = "extracted_invoices"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, index=True
    )
    created_by_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    document_upload_id: uuid.UUID = Field(foreign_key="document_uploads.id", nullable=False, unique=True)
    approved_by_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id")

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    organization: "Organization" = Relationship()
    created_by: "User" = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ExtractedInvoice.created_by_id]"))
    approved_by: Optional["User"] = Relationship(sa_relationship_kwargs=dict(foreign_keys="[ExtractedInvoice.approved_by_id]"))

    document_upload: "DocumentUpload" = Relationship(back_populates="extracted_invoice")


class ExtractedInvoiceCreate(ExtractedInvoiceBase):
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    document_upload_id: uuid.UUID


class ExtractedInvoiceUpdate(BaseModel):
    status: Optional[ExtractedInvoiceStatus] = None
    confidence_score: Optional[Decimal] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_vat_number: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    customer_vat_number: Optional[str] = None
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    line_items: Optional[List[Dict[str, Any]]] = None
    approved_at: Optional[datetime] = None
    approved_by_id: Optional[uuid.UUID] = None
    rejection_reason: Optional[str] = None


class ExtractedInvoicePublic(ExtractedInvoiceBase):
    id: uuid.UUID
    date_created: datetime
    document_upload: "DocumentUpload"


class ExtractedInvoicesPublic(BaseModel):
    data: List[ExtractedInvoicePublic]
    count: int
