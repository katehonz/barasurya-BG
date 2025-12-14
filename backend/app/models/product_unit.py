"""
ProductUnit model - мулти мерни единици за продукт с коефициенти за конверсия.
"""
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.measurement_unit import MeasurementUnit


class ProductUnitBase(BaseModel):
    """Base product unit fields."""
    conversion_factor: Decimal = Field(
        ..., max_digits=15, decimal_places=6,
        description="Conversion factor to base unit"
    )
    is_primary: bool = Field(default=False, description="Is this the primary unit")
    is_active: bool = Field(default=True, description="Is unit active for this product")
    barcode: Optional[str] = Field(default=None, max_length=50, description="Barcode for this unit")


class ProductUnit(ProductUnitBase, table=True):
    """ProductUnit database model."""
    __tablename__ = "product_units"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    product_id: UUID = Field(foreign_key="products.id", index=True)
    measurement_unit_id: UUID = Field(foreign_key="measurement_units.id", index=True)

    # Relationships
    product: "Product" = Relationship(back_populates="product_units")
    measurement_unit: "MeasurementUnit" = Relationship(back_populates="product_units")

    @staticmethod
    def convert(from_unit: "ProductUnit", to_unit: "ProductUnit", quantity: Decimal) -> Decimal:
        """Convert quantity from one unit to another."""
        # from_factor = 12.0 (box)
        # to_factor = 1.0 (liter)
        # quantity = 5 boxes
        # result = 5 * 12.0 / 1.0 = 60 liters
        return (quantity * from_unit.conversion_factor) / to_unit.conversion_factor


class ProductUnitCreate(ProductUnitBase):
    """Schema for creating a product unit."""
    product_id: UUID
    measurement_unit_id: UUID


class ProductUnitUpdate(BaseModel):
    """Schema for updating a product unit."""
    conversion_factor: Optional[Decimal] = None
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    barcode: Optional[str] = Field(default=None, max_length=50)


class ProductUnitPublic(ProductUnitBase):
    """Public product unit schema."""
    id: UUID
    product_id: UUID
    measurement_unit_id: UUID


class ProductUnitsPublic(SQLModel):
    """List of product units with count."""
    data: list[ProductUnitPublic]
    count: int
