"""
Lot model - партиди/серии с проследяване на срокове на годност.
"""
from datetime import date
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product


class LotBase(BaseModel):
    """Base lot fields."""
    lot_number: str = Field(..., max_length=50, description="Lot/batch number")
    manufacture_date: Optional[date] = Field(default=None, description="Manufacturing date")
    expiry_date: Optional[date] = Field(default=None, description="Expiry date")
    supplier_lot_number: Optional[str] = Field(default=None, max_length=50, description="Supplier's lot number")
    notes: Optional[str] = Field(default=None, description="Notes")
    is_active: bool = Field(default=True, description="Is lot active")


class Lot(LotBase, table=True):
    """Lot database model."""
    __tablename__ = "lots"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", index=True)
    product_id: UUID = Field(foreign_key="products.id", index=True)

    # Relationships
    product: "Product" = Relationship(back_populates="lots")

    def is_expired(self) -> bool:
        """Check if lot is expired."""
        if self.expiry_date is None:
            return False
        return date.today() > self.expiry_date

    def is_expiring_soon(self, days: int = 30) -> bool:
        """Check if lot is expiring within given days."""
        if self.expiry_date is None:
            return False
        threshold = date.today()
        from datetime import timedelta
        threshold = threshold + timedelta(days=days)
        return self.expiry_date <= threshold


class LotCreate(LotBase):
    """Schema for creating a lot."""
    organization_id: UUID
    product_id: UUID


class LotUpdate(BaseModel):
    """Schema for updating a lot."""
    lot_number: Optional[str] = Field(default=None, max_length=50)
    manufacture_date: Optional[date] = None
    expiry_date: Optional[date] = None
    supplier_lot_number: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class LotPublic(LotBase):
    """Public lot schema."""
    id: UUID
    organization_id: UUID
    product_id: UUID


class LotsPublic(SQLModel):
    """List of lots with count."""
    data: List[LotPublic]
    count: int
