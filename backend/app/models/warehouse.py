"""
Warehouse model - складове с методи за оценка на материалните запаси.
"""
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.stock_level import StockLevel
    from app.models.stock_movement import StockMovement
    from app.models.lot import Lot


# Costing methods
COSTING_METHODS = ["weighted_average", "fifo", "lifo"]


class WarehouseBase(BaseModel):
    """Base warehouse fields."""
    code: str = Field(..., max_length=20, description="Warehouse code")
    name: str = Field(..., max_length=200, description="Warehouse name")
    address: Optional[str] = Field(default=None, max_length=500, description="Address")
    city: Optional[str] = Field(default=None, max_length=100, description="City")
    postal_code: Optional[str] = Field(default=None, max_length=20, description="Postal code")
    country: str = Field(default="BG", max_length=3, description="Country code")
    is_active: bool = Field(default=True, description="Is warehouse active")
    notes: Optional[str] = Field(default=None, description="Notes")
    costing_method: str = Field(
        default="weighted_average",
        max_length=20,
        description="Costing method: weighted_average, fifo, lifo"
    )


class Warehouse(WarehouseBase, table=True):
    """Warehouse database model."""
    __tablename__ = "warehouses"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", index=True)

    # Relationships
    organization: "Organization" = Relationship(back_populates="warehouses")
    stock_levels: List["StockLevel"] = Relationship(back_populates="warehouse", cascade_delete=True)
    stock_movements: List["StockMovement"] = Relationship(
        back_populates="warehouse",
        sa_relationship_kwargs={"foreign_keys": "[StockMovement.warehouse_id]"}
    )

    @staticmethod
    def costing_method_name(method: str) -> str:
        """Get human-readable costing method name."""
        names = {
            "weighted_average": "Средно претеглена цена",
            "fifo": "FIFO (Първа входяща, първа изходяща)",
            "lifo": "LIFO (Последна входяща, първа изходяща)",
        }
        return names.get(method, "Неизвестен")


class WarehouseCreate(WarehouseBase):
    """Schema for creating a warehouse."""
    organization_id: UUID


class WarehouseUpdate(BaseModel):
    """Schema for updating a warehouse."""
    code: Optional[str] = Field(default=None, max_length=20)
    name: Optional[str] = Field(default=None, max_length=200)
    address: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    country: Optional[str] = Field(default=None, max_length=3)
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    costing_method: Optional[str] = Field(default=None, max_length=20)


class WarehousePublic(WarehouseBase):
    """Public warehouse schema."""
    id: UUID
    organization_id: UUID


class WarehousesPublic(SQLModel):
    """List of warehouses with count."""
    data: List[WarehousePublic]
    count: int
