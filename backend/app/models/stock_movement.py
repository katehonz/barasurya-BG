"""
StockMovement model - складови движения (приход, разход, трансфер).
"""
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.warehouse import Warehouse


# Movement types
MOVEMENT_TYPES = [
    "in",                  # Приход от доставчик
    "out",                 # Разход (продажба)
    "transfer",            # Прехвърляне между складове
    "adjustment",          # Корекция
    "surplus",             # Излишък при инвентаризация
    "shortage",            # Липса при инвентаризация
    "scrapping",           # Брак
    "production_receipt",  # Приход от производство
    "production_issue",    # Изписване за производство
    "opening_balance",     # Начално салдо
    "purchase",            # Покупка
    "sale",                # Продажба
]

MOVEMENT_STATUSES = ["draft", "confirmed", "cancelled"]


class StockMovementBase(BaseModel):
    """Base stock movement fields."""
    document_no: Optional[str] = Field(default=None, max_length=50, description="Document number")
    movement_type: str = Field(..., max_length=30, description="Type of movement")
    movement_date: date = Field(..., description="Movement date")
    status: str = Field(default="draft", max_length=20, description="Status: draft, confirmed, cancelled")
    notes: Optional[str] = Field(default=None, description="Notes")

    # Reference to source document
    reference_type: Optional[str] = Field(default=None, max_length=50, description="Source document type")
    reference_id: Optional[UUID] = Field(default=None, description="Source document ID")

    # Quantities and prices
    quantity: Decimal = Field(..., max_digits=15, decimal_places=4, description="Movement quantity")
    unit_cost: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=4,
        description="Unit cost (for incoming)"
    )
    unit_price: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=4,
        description="Unit price (for outgoing)"
    )
    total_amount: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=2,
        description="Total amount"
    )

    # Computed costs (filled by costing engine)
    computed_unit_cost: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=4,
        description="Computed unit cost"
    )
    computed_total_cost: Optional[Decimal] = Field(
        default=None, max_digits=15, decimal_places=2,
        description="Computed total cost"
    )


class StockMovement(StockMovementBase, table=True):
    """StockMovement database model."""
    __tablename__ = "stock_movements"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", index=True)
    product_id: UUID = Field(foreign_key="products.id", index=True)
    warehouse_id: UUID = Field(foreign_key="warehouses.id", index=True)
    to_warehouse_id: Optional[UUID] = Field(
        default=None, foreign_key="warehouses.id",
        description="Target warehouse (for transfers)"
    )
    lot_id: Optional[UUID] = Field(default=None, foreign_key="lots.id", description="Lot reference")

    # Relationships
    product: "Product" = Relationship()
    warehouse: "Warehouse" = Relationship(
        back_populates="stock_movements",
        sa_relationship_kwargs={"foreign_keys": "[StockMovement.warehouse_id]"}
    )
    to_warehouse: Optional["Warehouse"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[StockMovement.to_warehouse_id]"}
    )

    def is_incoming(self) -> bool:
        """Check if movement is incoming."""
        return self.movement_type in [
            "in", "surplus", "production_receipt", "opening_balance", "purchase"
        ]

    def is_outgoing(self) -> bool:
        """Check if movement is outgoing."""
        return self.movement_type in [
            "out", "shortage", "scrapping", "production_issue", "sale"
        ]

    def calculate_total(self) -> Decimal:
        """Calculate total amount."""
        if self.quantity and self.unit_price:
            return self.quantity * self.unit_price
        return Decimal("0")


class StockMovementCreate(StockMovementBase):
    """Schema for creating a stock movement."""
    organization_id: UUID
    product_id: UUID
    warehouse_id: UUID
    to_warehouse_id: Optional[UUID] = None
    lot_id: Optional[UUID] = None


class StockMovementUpdate(BaseModel):
    """Schema for updating a stock movement."""
    document_no: Optional[str] = Field(default=None, max_length=50)
    movement_type: Optional[str] = Field(default=None, max_length=30)
    movement_date: Optional[date] = None
    status: Optional[str] = Field(default=None, max_length=20)
    notes: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_cost: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None


class StockMovementPublic(StockMovementBase):
    """Public stock movement schema."""
    id: UUID
    organization_id: UUID
    product_id: UUID
    warehouse_id: UUID
    to_warehouse_id: Optional[UUID] = None
    lot_id: Optional[UUID] = None


class StockMovementsPublic(SQLModel):
    """List of stock movements with count."""
    data: List[StockMovementPublic]
    count: int
