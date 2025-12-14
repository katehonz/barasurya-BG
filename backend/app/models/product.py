"""
Product model - артикули (стоки, материали, услуги, произведена продукция).
"""
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.product_unit import ProductUnit
    from app.models.lot import Lot
    from app.models.stock_level import StockLevel


# Product categories
PRODUCT_CATEGORIES = ["goods", "materials", "services", "produced"]


class ProductBase(BaseModel):
    """Base product fields."""
    name: str = Field(..., max_length=255, description="Product name")
    sku: str = Field(..., max_length=50, description="Stock Keeping Unit code")
    description: Optional[str] = Field(default=None, description="Product description")
    category: str = Field(
        default="goods",
        max_length=20,
        description="Category: goods, materials, services, produced"
    )

    # Pricing
    price: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2, description="Selling price")
    cost: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2, description="Cost price")

    # Unit and tax
    unit: str = Field(default="бр.", max_length=20, description="Default unit")
    barcode: Optional[str] = Field(default=None, max_length=50, description="Product barcode")
    tax_rate: Decimal = Field(default=Decimal("20"), max_digits=5, decimal_places=2, description="VAT rate %")

    # Flags
    is_active: bool = Field(default=True, description="Is product active")
    track_inventory: bool = Field(default=True, description="Track inventory levels")

    # Opening balances
    opening_quantity: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=4, description="Opening stock quantity")
    opening_cost: Decimal = Field(default=Decimal("0"), max_digits=15, decimal_places=2, description="Opening stock value")

    # Account references (for accounting integration)
    account_id: Optional[UUID] = Field(default=None, description="Inventory account (304, 302, 303)")
    expense_account_id: Optional[UUID] = Field(default=None, description="Expense account (702, 601, 611)")
    revenue_account_id: Optional[UUID] = Field(default=None, description="Revenue account (702)")

    # CN Nomenclature for Intrastat
    cn_code: Optional[str] = Field(default=None, max_length=10, description="Combined Nomenclature code (KN8)")


class Product(ProductBase, table=True):
    """Product database model."""
    __tablename__ = "products"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", index=True)

    # Relationships
    organization: "Organization" = Relationship(back_populates="products")
    product_units: List["ProductUnit"] = Relationship(back_populates="product", cascade_delete=True)
    lots: List["Lot"] = Relationship(back_populates="product", cascade_delete=True)
    stock_levels: List["StockLevel"] = Relationship(back_populates="product", cascade_delete=True)


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    organization_id: UUID


class ProductUpdate(BaseModel):
    """Schema for updating a product."""
    name: Optional[str] = Field(default=None, max_length=255)
    sku: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=20)
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    unit: Optional[str] = Field(default=None, max_length=20)
    barcode: Optional[str] = Field(default=None, max_length=50)
    tax_rate: Optional[Decimal] = None
    is_active: Optional[bool] = None
    track_inventory: Optional[bool] = None
    cn_code: Optional[str] = Field(default=None, max_length=10)


class ProductPublic(ProductBase):
    """Public product schema."""
    id: UUID
    organization_id: UUID


class ProductsPublic(SQLModel):
    """List of products with count."""
    data: List[ProductPublic]
    count: int
