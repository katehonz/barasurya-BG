"""
StockLevel model - складови наличности по продукт и склад.
"""
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.warehouse import Warehouse


class StockLevelBase(BaseModel):
    """Base stock level fields."""
    # Quantities
    quantity_on_hand: Decimal = Field(
        default=Decimal("0"), max_digits=15, decimal_places=4,
        description="Quantity on hand"
    )
    quantity_reserved: Decimal = Field(
        default=Decimal("0"), max_digits=15, decimal_places=4,
        description="Reserved quantity"
    )
    quantity_available: Decimal = Field(
        default=Decimal("0"), max_digits=15, decimal_places=4,
        description="Available quantity (on_hand - reserved)"
    )
    minimum_quantity: Decimal = Field(
        default=Decimal("0"), max_digits=15, decimal_places=4,
        description="Minimum quantity threshold"
    )
    reorder_point: Decimal = Field(
        default=Decimal("0"), max_digits=15, decimal_places=4,
        description="Reorder point"
    )

    # Costs
    average_cost: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=4,
        description="Average cost per unit"
    )
    last_cost: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=4,
        description="Last purchase cost"
    )
    total_value: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=2,
        description="Total inventory value"
    )


class StockLevel(StockLevelBase, table=True):
    """StockLevel database model."""
    __tablename__ = "stock_levels"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", index=True)
    product_id: UUID = Field(foreign_key="products.id", index=True)
    warehouse_id: UUID = Field(foreign_key="warehouses.id", index=True)

    # Relationships
    product: "Product" = Relationship(back_populates="stock_levels")
    warehouse: "Warehouse" = Relationship(back_populates="stock_levels")

    def calculate_available(self) -> Decimal:
        """Calculate available quantity."""
        return self.quantity_on_hand - self.quantity_reserved

    def calculate_total_value(self) -> Decimal:
        """Calculate total inventory value."""
        if self.quantity_on_hand and self.average_cost:
            return self.quantity_on_hand * self.average_cost
        return Decimal("0")

    def is_below_minimum(self) -> bool:
        """Check if stock is below minimum."""
        return self.quantity_available < self.minimum_quantity

    def needs_reorder(self) -> bool:
        """Check if stock needs to be reordered."""
        return self.quantity_available <= self.reorder_point


class StockLevelCreate(StockLevelBase):
    """Schema for creating a stock level."""
    organization_id: UUID
    product_id: UUID
    warehouse_id: UUID


class StockLevelUpdate(BaseModel):
    """Schema for updating a stock level."""
    quantity_on_hand: Optional[Decimal] = None
    quantity_reserved: Optional[Decimal] = None
    minimum_quantity: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    average_cost: Optional[Decimal] = None
    last_cost: Optional[Decimal] = None


class StockLevelPublic(StockLevelBase):
    """Public stock level schema."""
    id: UUID
    organization_id: UUID
    product_id: UUID
    warehouse_id: UUID


class StockLevelsPublic(SQLModel):
    """List of stock levels with count."""
    data: List[StockLevelPublic]
    count: int
