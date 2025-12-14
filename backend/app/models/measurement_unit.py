"""
MeasurementUnit model - стандартизирани мерни единици (SAF-T съвместими).
"""
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.product_unit import ProductUnit


# Standard measurement units according to SAF-T
STANDARD_UNITS = {
    "kg": {"name_bg": "Килограм", "name_en": "Kilogram", "symbol": "kg"},
    "g": {"name_bg": "Грам", "name_en": "Gram", "symbol": "g"},
    "t": {"name_bg": "Тон", "name_en": "Ton", "symbol": "t"},
    "l": {"name_bg": "Литър", "name_en": "Liter", "symbol": "l"},
    "ml": {"name_bg": "Милилитър", "name_en": "Milliliter", "symbol": "ml"},
    "m": {"name_bg": "Метър", "name_en": "Meter", "symbol": "m"},
    "cm": {"name_bg": "Сантиметър", "name_en": "Centimeter", "symbol": "cm"},
    "mm": {"name_bg": "Милиметър", "name_en": "Millimeter", "symbol": "mm"},
    "m2": {"name_bg": "Квадратен метър", "name_en": "Square meter", "symbol": "m²"},
    "m3": {"name_bg": "Кубичен метър", "name_en": "Cubic meter", "symbol": "m³"},
    "p/st": {"name_bg": "Брой", "name_en": "Piece", "symbol": "бр."},
    "pair": {"name_bg": "Двойка", "name_en": "Pair", "symbol": "двойка"},
    "set": {"name_bg": "Комплект", "name_en": "Set", "symbol": "компл."},
    "pack": {"name_bg": "Пакет", "name_en": "Package", "symbol": "пак."},
    "box": {"name_bg": "Кутия", "name_en": "Box", "symbol": "кут."},
    "pallet": {"name_bg": "Палет", "name_en": "Pallet", "symbol": "палет"},
    "kWh": {"name_bg": "Киловатчас", "name_en": "Kilowatt-hour", "symbol": "kWh"},
    "hour": {"name_bg": "Час", "name_en": "Hour", "symbol": "ч."},
}


class MeasurementUnitBase(BaseModel):
    """Base measurement unit fields."""
    code: str = Field(..., max_length=20, description="Unit code (kg, l, m, etc.)")
    name_bg: str = Field(..., max_length=100, description="Bulgarian name")
    name_en: Optional[str] = Field(default=None, max_length=100, description="English name")
    symbol: str = Field(..., max_length=20, description="Display symbol")
    is_base: bool = Field(default=False, description="Is this a base unit")
    is_active: bool = Field(default=True, description="Is unit active")


class MeasurementUnit(MeasurementUnitBase, table=True):
    """MeasurementUnit database model."""
    __tablename__ = "measurement_units"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", index=True)

    # Relationships
    organization: "Organization" = Relationship(back_populates="measurement_units")
    product_units: List["ProductUnit"] = Relationship(back_populates="measurement_unit")


class MeasurementUnitCreate(MeasurementUnitBase):
    """Schema for creating a measurement unit."""
    organization_id: UUID


class MeasurementUnitUpdate(BaseModel):
    """Schema for updating a measurement unit."""
    code: Optional[str] = Field(default=None, max_length=20)
    name_bg: Optional[str] = Field(default=None, max_length=100)
    name_en: Optional[str] = Field(default=None, max_length=100)
    symbol: Optional[str] = Field(default=None, max_length=20)
    is_base: Optional[bool] = None
    is_active: Optional[bool] = None


class MeasurementUnitPublic(MeasurementUnitBase):
    """Public measurement unit schema."""
    id: UUID
    organization_id: UUID


class MeasurementUnitsPublic(SQLModel):
    """List of measurement units with count."""
    data: List[MeasurementUnitPublic]
    count: int
