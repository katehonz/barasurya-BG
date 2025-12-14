"""
Purchase Order models - поръчки за доставка.
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
from app.models.purchase_order_line import (
    PurchaseOrderLineCreate,
    PurchaseOrderLineUpdate,
    PurchaseOrderLinePublic,
)

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.contraagent import Contraagent
    from app.models.user import User
    from app.models.warehouse import Warehouse
    from app.models.invoice import Invoice
    from .purchase_order_line import PurchaseOrderLine


class PurchaseOrderStatus(str, enum.Enum):
    """Purchase order status workflow."""

    DRAFT = "draft"
    SENT = "sent"
    CONFIRMED = "confirmed"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CANCELLED = "cancelled"
    CLOSED = "closed"


class PurchaseOrderPriority(str, enum.Enum):
    """Purchase order priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class PurchaseOrderBase(BaseModel):
    """Base purchase order fields."""

    order_no: str = Field(
        max_length=50, index=True, description="Purchase order number"
    )
    order_date: date = Field(description="Order date")
    expected_delivery_date: Optional[date] = Field(
        default=None, description="Expected delivery date"
    )

    # Contraagent information
    contraagent_reference: Optional[str] = Field(
        default=None, max_length=100, description="Contraagent reference number"
    )
    contraagent_contact: Optional[str] = Field(
        default=None, max_length=255, description="Contraagent contact person"
    )

    # Delivery information
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
    status: PurchaseOrderStatus = Field(default=PurchaseOrderStatus.DRAFT)
    priority: PurchaseOrderPriority = Field(default=PurchaseOrderPriority.NORMAL)

    # Notes and terms
    notes: Optional[str] = Field(default=None, max_length=2000)
    payment_terms: Optional[str] = Field(default=None, max_length=500)
    delivery_terms: Optional[str] = Field(default=None, max_length=500)

    # Internal fields
    internal_notes: Optional[str] = Field(default=None, max_length=2000)
    requested_by: Optional[str] = Field(
        default=None, max_length=255, description="Employee who requested the order"
    )


class PurchaseOrder(PurchaseOrderBase, table=True):
    """Purchase order database model."""

    __tablename__ = "purchase_orders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)
    created_by_id: uuid.UUID = Field(foreign_key="user.id")
    contraagent_id: uuid.UUID = Field(foreign_key="contraagent.id")
    warehouse_id: Optional[uuid.UUID] = Field(default=None)  # FK disabled - table doesn't exist

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    sent_date: Optional[datetime] = Field(default=None)
    confirmed_date: Optional[datetime] = Field(default=None)
    received_date: Optional[datetime] = Field(default=None)

    # Document UID for unique identification
    document_uid: str = Field(max_length=100, unique=True, index=True)

    # Link to contraagent invoice (when received)
    contraagent_invoice_id: Optional[uuid.UUID] = Field(default=None) # Changed from supplier_invoice_id and FK disabled - table doesn't exist

    # Relationships
    organization: "Organization" = Relationship(back_populates="purchase_orders")
    created_by: "User" = Relationship()
    contraagent: "Contraagent" = Relationship(back_populates="purchase_orders")
    # Note: warehouse and contraagent_invoice relationships disabled - tables don't exist yet
    purchase_order_lines: List["PurchaseOrderLine"] = Relationship(
        back_populates="purchase_order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema for creating a purchase order."""

    contraagent_id: uuid.UUID
    warehouse_id: Optional[uuid.UUID] = None
    purchase_order_lines: List[PurchaseOrderLineCreate]


class PurchaseOrderUpdate(SQLModel):
    """Schema for updating a purchase order."""

    order_date: Optional[date] = None
    expected_delivery_date: Optional[date] = None
    contraagent_reference: Optional[str] = None
    contraagent_contact: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_instructions: Optional[str] = None
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    currency_code: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    status: Optional[PurchaseOrderStatus] = None
    priority: Optional[PurchaseOrderPriority] = None
    notes: Optional[str] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    internal_notes: Optional[str] = None
    requested_by: Optional[str] = None
    warehouse_id: Optional[uuid.UUID] = None
    purchase_order_lines: Optional[List[PurchaseOrderLineUpdate]] = None


class PurchaseOrderPublic(PurchaseOrderBase):
    """Public purchase order schema."""

    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    contraagent_id: uuid.UUID
    contraagent_name: str
    warehouse_id: Optional[uuid.UUID] = None
    warehouse_name: Optional[str] = None
    date_created: datetime
    date_updated: datetime
    sent_date: Optional[datetime] = None
    confirmed_date: Optional[datetime] = None
    received_date: Optional[datetime] = None
    document_uid: str
    purchase_order_lines: List[PurchaseOrderLinePublic]


class PurchaseOrdersPublic(BaseModel):
    """List of purchase orders with count."""

    data: List[PurchaseOrderPublic]
    count: int

