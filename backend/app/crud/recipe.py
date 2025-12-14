"""
CRUD операции за производствени рецепти.
"""
import uuid
from typing import Sequence

from sqlmodel import Session, select

from app.models.recipe import Recipe, RecipeCreate, RecipeUpdate
from app.models.recipe_item import RecipeItem, RecipeItemCreate, RecipeItemUpdate
from app.utils import utcnow


def create_recipe(
    *,
    session: Session,
    recipe_in: RecipeCreate,
    organization_id: uuid.UUID,
    created_by_id: uuid.UUID,
) -> Recipe:
    """Създава нова рецепта."""
    db_recipe = Recipe.model_validate(
        recipe_in,
        update={
            "organization_id": organization_id,
            "created_by_id": created_by_id,
        },
    )
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe


def get_recipe(
    *, session: Session, recipe_id: uuid.UUID, organization_id: uuid.UUID
) -> Recipe | None:
    """Връща рецепта по ID."""
    statement = select(Recipe).where(
        Recipe.id == recipe_id,
        Recipe.organization_id == organization_id,
    )
    return session.exec(statement).first()


def get_recipes(
    *,
    session: Session,
    organization_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
) -> Sequence[Recipe]:
    """Връща списък с рецепти за организацията."""
    statement = select(Recipe).where(Recipe.organization_id == organization_id)
    if is_active is not None:
        statement = statement.where(Recipe.is_active == is_active)
    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()


def get_recipes_count(
    *, session: Session, organization_id: uuid.UUID, is_active: bool | None = None
) -> int:
    """Връща броя рецепти за организацията."""
    statement = select(Recipe).where(Recipe.organization_id == organization_id)
    if is_active is not None:
        statement = statement.where(Recipe.is_active == is_active)
    return len(session.exec(statement).all())


def update_recipe(
    *, session: Session, db_recipe: Recipe, recipe_in: RecipeUpdate
) -> Recipe:
    """Обновява рецепта."""
    update_data = recipe_in.model_dump(exclude_unset=True)
    update_data["date_updated"] = utcnow()
    db_recipe.sqlmodel_update(update_data)
    session.add(db_recipe)
    session.commit()
    session.refresh(db_recipe)
    return db_recipe


def delete_recipe(*, session: Session, db_recipe: Recipe) -> None:
    """Изтрива рецепта."""
    session.delete(db_recipe)
    session.commit()


# RecipeItem CRUD operations


def create_recipe_item(
    *, session: Session, recipe_id: uuid.UUID, item_in: RecipeItemCreate
) -> RecipeItem:
    """Добавя компонент към рецепта."""
    db_item = RecipeItem.model_validate(item_in, update={"recipe_id": recipe_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_recipe_item(
    *, session: Session, item_id: uuid.UUID, recipe_id: uuid.UUID
) -> RecipeItem | None:
    """Връща компонент по ID."""
    statement = select(RecipeItem).where(
        RecipeItem.id == item_id,
        RecipeItem.recipe_id == recipe_id,
    )
    return session.exec(statement).first()


def get_recipe_items(
    *, session: Session, recipe_id: uuid.UUID
) -> Sequence[RecipeItem]:
    """Връща всички компоненти на рецепта."""
    statement = (
        select(RecipeItem)
        .where(RecipeItem.recipe_id == recipe_id)
        .order_by(RecipeItem.line_no)
    )
    return session.exec(statement).all()


def update_recipe_item(
    *, session: Session, db_item: RecipeItem, item_in: RecipeItemUpdate
) -> RecipeItem:
    """Обновява компонент на рецепта."""
    update_data = item_in.model_dump(exclude_unset=True)
    db_item.sqlmodel_update(update_data)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_recipe_item(*, session: Session, db_item: RecipeItem) -> None:
    """Изтрива компонент от рецепта."""
    session.delete(db_item)
    session.commit()


def get_recipes_by_output_item(
    *, session: Session, organization_id: uuid.UUID, output_item_id: uuid.UUID
) -> Sequence[Recipe]:
    """Връща рецептите за даден изходен продукт."""
    statement = select(Recipe).where(
        Recipe.organization_id == organization_id,
        Recipe.output_item_id == output_item_id,
    )
    return session.exec(statement).all()
