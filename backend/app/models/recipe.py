"""
Производствена рецепта (Bill of Materials) за крайни продукти.
Базирано на CyberERP manufacturing module.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.recipe_item import RecipeItem


class RecipeBase(BaseModel):
    """Базов модел за рецепта."""
    code: str = Field(max_length=50, description="Уникален код на рецептата")
    name: str = Field(max_length=120, description="Наименование")
    description: str | None = Field(default=None, max_length=500)
    output_quantity: Decimal = Field(default=Decimal("1"), ge=0, description="Изходно количество")
    unit: str = Field(default="бр.", max_length=20, description="Мерна единица")
    version: str = Field(default="1.0", max_length=20, description="Версия на рецептата")
    is_active: bool = Field(default=True, description="Активна рецепта")
    production_cost: Decimal = Field(default=Decimal("0"), ge=0, description="Производствена цена")
    notes: str | None = Field(default=None, max_length=1000)


class RecipeCreate(RecipeBase):
    """Схема за създаване на рецепта."""
    output_item_id: uuid.UUID = Field(description="ID на изходния продукт")


class RecipeUpdate(SQLModel):
    """Схема за обновяване на рецепта."""
    code: str | None = Field(default=None, max_length=50)
    name: str | None = Field(default=None, max_length=120)
    description: str | None = None
    output_quantity: Decimal | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=20)
    version: str | None = Field(default=None, max_length=20)
    is_active: bool | None = None
    production_cost: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None


class Recipe(RecipeBase, table=True):
    """Производствена рецепта."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    output_item_id: uuid.UUID = Field(
        foreign_key="item.id", nullable=False, description="Изходен продукт"
    )

    # Relationships
    organization: "Organization" = Relationship()
    created_by: "User" = Relationship()
    output_item: "Item" = Relationship()
    recipe_items: List["RecipeItem"] = Relationship(
        back_populates="recipe", cascade_delete=True
    )


class RecipePublic(RecipeBase):
    """Публична схема за рецепта."""
    id: uuid.UUID
    output_item_id: uuid.UUID
    organization_id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class RecipePublicWithItems(RecipePublic):
    """Публична схема за рецепта с включени компоненти."""
    recipe_items: List["RecipeItemPublic"] = []


class RecipesPublic(SQLModel):
    """Списък с рецепти."""
    data: List[RecipePublic]
    count: int


# Forward reference for RecipeItemPublic
from app.models.recipe_item import RecipeItemPublic
RecipePublicWithItems.model_rebuild()
