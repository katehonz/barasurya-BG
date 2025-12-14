"""
Quotation models - оферти за продажба.
"""

import uuid
import enum
from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING
from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel
from app.utils import utcnow

# Import line schemas for Create/Update (needed at runtime)
from app.models.quotation_line import (
    QuotationLineCreate,
    QuotationLineUpdate,
    QuotationLinePublic,
)

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.contraagent import Contraagent
    from app.models.user import User
    from app.models.invoice import Invoice
    from .quotation_line import QuotationLine


class QuotationStatus(str, enum.Enum):
    """Quotation status workflow."""

    DRAFT = "draft"
    SENT = "sent"
    OPEN = "open"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED_TO_INVOICE = "converted_to_invoice"
    CANCELLED = "cancelled"


class QuotationPriority(str, enum.Enum):
    """Quotation priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class QuotationBase(BaseModel):
    """Base quotation fields."""

    quotation_no: str = Field(max_length=50, index=True, description="Quotation number")
    quotation_date: date = Field(description="Quotation date")
    valid_until: date = Field(description="Valid until date")

    # Contraagent information
    contraagent_reference: Optional[str] = Field(
        default=None, max_length=100, description="Contraagent reference/PO number"
    )
    contraagent_contact: Optional[str] = Field(
        default=None, max_length=255, description="Contraagent contact person"
    )

    # Billing and delivery information
    billing_address: Optional[str] = Field(
        default=None, max_length=500, description="Billing address"
    )
    delivery_address: Optional[str] = Field(
        default=None, max_length=500, description="Delivery address"
    )
    delivery_instructions: Optional[str] = Field(
        default=None, max_length=1000, description="Delivery instructions"
    )

    # Financial information
    subtotal: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    tax_amount: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    total_amount: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2)
    discount_amount: Decimal = Field(
        default=Decimal("0"), max_digits=15, decimal_places=2
    )
    discount_percent: Decimal = Field(
        default=Decimal("0"), max_digits=5, decimal_places=2
    )

    # Currency
    currency_code: str = Field(default="BGN", max_length=3, description="Currency code")
    exchange_rate: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=6
    )

    # Status and priority
    status: QuotationStatus = Field(default=QuotationStatus.DRAFT)
    priority: QuotationPriority = Field(default=QuotationPriority.NORMAL)

    # Notes and terms
    notes: Optional[str] = Field(default=None, max_length=2000)
    payment_terms: Optional[str] = Field(default=None, max_length=500)
    delivery_terms: Optional[str] = Field(default=None, max_length=500)
    warranty_terms: Optional[str] = Field(default=None, max_length=500)

    # Internal fields
    internal_notes: Optional[str] = Field(default=None, max_length=2000)
    sales_person: Optional[str] = Field(
        default=None, max_length=255, description="Sales person responsible"
    )

    # Follow-up
    follow_up_date: Optional[date] = Field(default=None, description="Follow-up date")
    rejection_reason: Optional[str] = Field(
        default=None, max_length=500, description="Reason for rejection"
    )


class Quotation(QuotationBase, table=True):
    """Quotation database model."""

    __tablename__ = "quotations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)
    created_by_id: uuid.UUID = Field(foreign_key="user.id")
    contraagent_id: uuid.UUID = Field(foreign_key="contraagent.id")

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    sent_date: Optional[datetime] = Field(default=None)
    accepted_date: Optional[datetime] = Field(default=None)
    rejected_date: Optional[datetime] = Field(default=None)

    # Document UID for unique identification
    document_uid: str = Field(max_length=100, unique=True, index=True)

    # Link to invoice (when converted)
    invoice_id: Optional[uuid.UUID] = Field(default=None)  # FK disabled - table doesn't exist

    # Probability of winning (percentage)
    probability: Optional[Decimal] = Field(
        default=None, max_digits=5, decimal_places=2, description="Win probability %"
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="quotations")
    created_by: "User" = Relationship()
    contraagent: "Contraagent" = Relationship(back_populates="quotations")
    # Note: invoice relationship disabled - table doesn't exist yet
    quotation_lines: List["QuotationLine"] = Relationship(
        back_populates="quotation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class QuotationCreate(QuotationBase):
    """Schema for creating a quotation."""

    contraagent_id: uuid.UUID
    probability: Optional[Decimal] = None
    quotation_lines: List[QuotationLineCreate]


class QuotationUpdate(SQLModel):
    """Schema for updating a quotation."""

    quotation_date: Optional[date] = None
    valid_until: Optional[date] = None
    contraagent_reference: Optional[str] = None
    contraagent_contact: Optional[str] = None
    billing_address: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_instructions: Optional[str] = None
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    currency_code: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    status: Optional[QuotationStatus] = None
    priority: Optional[QuotationPriority] = None
    notes: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    warranty_terms: Optional[str] = None
    internal_notes: Optional[str] = None
    sales_person: Optional[str] = None
    follow_up_date: Optional[date] = None
    rejection_reason: Optional[str] = None
    probability: Optional[Decimal] = None
    quotation_lines: Optional[List[QuotationLineUpdate]] = None


class QuotationPublic(QuotationBase):
    """Public quotation schema."""

    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    contraagent_id: uuid.UUID
    contraagent_name: str
    date_created: datetime
    date_updated: datetime
    sent_date: Optional[datetime] = None
    accepted_date: Optional[datetime] = None
    rejected_date: Optional[datetime] = None
    document_uid: str
    probability: Optional[Decimal] = None
    quotation_lines: List[QuotationLinePublic]


class QuotationsPublic(BaseModel):
    """List of quotations with count."""

    data: List[QuotationPublic]
    count: int
