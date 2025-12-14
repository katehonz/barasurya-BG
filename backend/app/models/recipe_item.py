"""
Суровина/компонент в производствена рецепта.
Базирано на CyberERP RecipeItem.
"""
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.recipe import Recipe


class RecipeItemBase(SQLModel):
    """Базов модел за компонент на рецепта."""
    line_no: int = Field(default=10, description="Пореден номер на реда")
    description: str | None = Field(default=None, max_length=255, description="Описание")
    quantity: Decimal = Field(ge=0, description="Количество")
    unit: str = Field(default="бр.", max_length=20, description="Мерна единица")
    wastage_percent: Decimal = Field(
        default=Decimal("0"), ge=0, le=100, description="Процент брак/загуба"
    )
    cost: Decimal = Field(default=Decimal("0"), ge=0, description="Цена на компонента")
    notes: str | None = Field(default=None, max_length=500)


class RecipeItemCreate(RecipeItemBase):
    """Схема за създаване на компонент."""
    item_id: uuid.UUID = Field(description="ID на материала/артикула")


class RecipeItemUpdate(SQLModel):
    """Схема за обновяване на компонент."""
    line_no: int | None = None
    description: str | None = None
    quantity: Decimal | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=20)
    wastage_percent: Decimal | None = Field(default=None, ge=0, le=100)
    cost: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None


class RecipeItem(RecipeItemBase, table=True):
    """Компонент в производствена рецепта."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    recipe_id: uuid.UUID = Field(
        foreign_key="recipe.id", nullable=False, ondelete="CASCADE", index=True
    )
    item_id: uuid.UUID = Field(foreign_key="item.id", nullable=False)

    # Relationships
    recipe: "Recipe" = Relationship(back_populates="recipe_items")
    item: "Item" = Relationship()

    @property
    def effective_quantity(self) -> Decimal:
        """Изчислява ефективното количество с включен процент брак."""
        wastage_multiplier = 1 + (self.wastage_percent / 100)
        return self.quantity * wastage_multiplier

    @property
    def total_cost(self) -> Decimal:
        """Изчислява общата цена на компонента."""
        return self.effective_quantity * self.cost


class RecipeItemPublic(RecipeItemBase):
    """Публична схема за компонент."""
    id: uuid.UUID
    recipe_id: uuid.UUID
    item_id: uuid.UUID


class RecipeItemsPublic(SQLModel):
    """Списък с компоненти."""
    data: list[RecipeItemPublic]
    count: int
