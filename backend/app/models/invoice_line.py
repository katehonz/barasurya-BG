import uuid
from typing import Optional, TYPE_CHECKING
from decimal import Decimal

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.item import Item, ItemPublic
    from app.models.organization import Organization
    from app.models.user import User
    from .invoice import Invoice


class InvoiceLineBase(BaseModel):
    description: str
    quantity: Decimal = Field(max_digits=10, decimal_places=2)
    unit_of_measure: str = Field(default="бр.", max_length=10)
    unit_price: Decimal = Field(max_digits=10, decimal_places=2)
    discount_percent: Decimal = Field(default=0, max_digits=5, decimal_places=2)
    tax_rate: Decimal = Field(default=20, max_digits=5, decimal_places=2)


class InvoiceLine(InvoiceLineBase, table=True):
    __tablename__ = "invoice_lines"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    line_no: int

    discount_amount: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    subtotal: Decimal = Field(max_digits=10, decimal_places=2)
    tax_amount: Decimal = Field(max_digits=10, decimal_places=2)
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    
    notes: Optional[str] = None

    invoice_id: uuid.UUID = Field(foreign_key="invoices.id", nullable=False)
    invoice: "Invoice" = Relationship(back_populates="invoice_lines")

    product_id: Optional[uuid.UUID] = Field(default=None, foreign_key="items.id")
    product: Optional["Item"] = Relationship()


class InvoiceLineCreate(InvoiceLineBase):
    product_id: Optional[uuid.UUID] = None


class InvoiceLineUpdate(SQLModel):
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    # ... other fields


class InvoiceLinePublic(InvoiceLineBase):
    id: uuid.UUID
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    product: Optional["ItemPublic"] = None

class InvoiceLinesPublic(BaseModel):
    data: list[InvoiceLinePublic]
    count: int