"""
API routes за производствени рецепти.
"""
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import func, select

from app.api.deps import (
    CurrentMembership,
    CurrentOrganization,
    CurrentUser,
    SessionDep,
)
from app.crud.recipe import (
    create_recipe,
    create_recipe_item,
    delete_recipe,
    delete_recipe_item,
    get_recipe,
    get_recipe_item,
    get_recipe_items,
    update_recipe,
    update_recipe_item,
)
from app.models import (
    BaseModelUpdate,
    Product, # Changed from Item
    Message,
    OrganizationRole,
    has_role_or_higher,
)
from app.models.recipe import (
    Recipe,
    RecipeCreate,
    RecipePublic,
    RecipePublicWithItems,
    RecipesPublic,
    RecipeUpdate,
)
from app.models.recipe_item import (
    RecipeItem,
    RecipeItemCreate,
    RecipeItemPublic,
    RecipeItemsPublic,
    RecipeItemUpdate,
)

router = APIRouter(prefix="/recipes", tags=["recipes"])


# --- Recipe routes ---


@router.get("/", response_model=RecipesPublic)
def read_recipes(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
) -> Any:
    """
    Retrieve recipes for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(Recipe)
        .where(Recipe.organization_id == current_org.id)
    )
    if is_active is not None:
        count_statement = count_statement.where(Recipe.is_active == is_active)
    count = session.exec(count_statement).one()

    statement = (
        select(Recipe)
        .where(Recipe.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    if is_active is not None:
        statement = statement.where(Recipe.is_active == is_active)
    recipes = session.exec(statement).all()

    return RecipesPublic(data=recipes, count=count)


@router.get("/{recipe_id}", response_model=RecipePublicWithItems)
def read_recipe(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    recipe_id: uuid.UUID,
) -> Any:
    """
    Get recipe by ID with all items.
    """
    statement = (
        select(Recipe)
        .options(selectinload(Recipe.recipe_items))
        .where(
            Recipe.id == recipe_id,
            Recipe.organization_id == current_org.id,
        )
    )
    recipe = session.exec(statement).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецептата не е намерена")
    return recipe


@router.post("/", response_model=RecipePublic)
def create_recipe_endpoint(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    recipe_in: RecipeCreate,
) -> Any:
    """
    Create new recipe. Requires at least member role.
    """
    # Validate output_item_id belongs to organization
    output_product = session.get(Product, recipe_in.output_item_id) # Changed from output_item and Item
    if not output_product: # Changed from output_item
        raise HTTPException(status_code=404, detail="Изходният продукт не е намерен")
    if output_product.organization_id != current_org.id: # Changed from output_item
        raise HTTPException(
            status_code=403,
            detail="Изходният продукт принадлежи на друга организация",
        )

    # Check for unique code within organization
    existing = session.exec(
        select(Recipe).where(
            Recipe.organization_id == current_org.id,
            Recipe.code == recipe_in.code,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Рецепта с код '{recipe_in.code}' вече съществува",
        )

    recipe = create_recipe(
        session=session,
        recipe_in=recipe_in,
        organization_id=current_org.id,
        created_by_id=current_user.id,
    )
    return recipe


@router.put("/{recipe_id}", response_model=RecipePublic)
def update_recipe_endpoint(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    recipe_id: uuid.UUID,
    recipe_in: RecipeUpdate,
) -> Any:
    """
    Update a recipe. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Изисква се роля мениджър")

    recipe = get_recipe(
        session=session, recipe_id=recipe_id, organization_id=current_org.id
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецептата не е намерена")

    # Check for unique code if changing
    if recipe_in.code and recipe_in.code != recipe.code:
        existing = session.exec(
            select(Recipe).where(
                Recipe.organization_id == current_org.id,
                Recipe.code == recipe_in.code,
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Рецепта с код '{recipe_in.code}' вече съществува",
            )

    recipe = update_recipe(session=session, db_recipe=recipe, recipe_in=recipe_in)
    return recipe


@router.delete("/{recipe_id}")
def delete_recipe_endpoint(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    recipe_id: uuid.UUID,
) -> Message:
    """
    Delete a recipe. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Изисква се роля мениджър")

    recipe = get_recipe(
        session=session, recipe_id=recipe_id, organization_id=current_org.id
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецептата не е намерена")

    delete_recipe(session=session, db_recipe=recipe)
    return Message(message="Рецептата е изтрита успешно")


@router.put("/{recipe_id}/activate", response_model=RecipePublic)
def activate_recipe(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    recipe_id: uuid.UUID,
) -> Any:
    """
    Activate a recipe. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Изисква се роля мениджър")

    recipe = get_recipe(
        session=session, recipe_id=recipe_id, organization_id=current_org.id
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецептата не е намерена")

    recipe.is_active = True
    recipe.sqlmodel_update(BaseModelUpdate().model_dump())
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


@router.put("/{recipe_id}/deactivate", response_model=RecipePublic)
def deactivate_recipe(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    recipe_id: uuid.UUID,
) -> Any:
    """
    Deactivate a recipe. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Изисква се роля мениджър")

    recipe = get_recipe(
        session=session, recipe_id=recipe_id, organization_id=current_org.id
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецептата не е намерена")

    recipe.is_active = False
    recipe.sqlmodel_update(BaseModelUpdate().model_dump())
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


# --- RecipeItem routes ---


@router.get("/{recipe_id}/items", response_model=RecipeItemsPublic)
def read_recipe_items(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    recipe_id: uuid.UUID,
) -> Any:
    """
    Retrieve all items for a recipe.
    """
    recipe = get_recipe(
        session=session, recipe_id=recipe_id, organization_id=current_org.id
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецептата не е намерена")

    items = get_recipe_items(session=session, recipe_id=recipe_id)
    return RecipeItemsPublic(data=items, count=len(items))


@router.post("/{recipe_id}/items", response_model=RecipeItemPublic)
def create_recipe_item_endpoint(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    recipe_id: uuid.UUID,
    item_in: RecipeItemCreate, # item_in still has item_id, will be product_id now
) -> Any:
    """
    Add item to a recipe. Requires at least member role.
    """
    recipe = get_recipe(
        session=session, recipe_id=recipe_id, organization_id=current_org.id
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецептата не е намерена")

    # Validate product belongs to organization
    product = session.get(Product, item_in.product_id) # Changed from item and item_in.item_id
    if not product:
        raise HTTPException(status_code=404, detail="Продуктът не е намерен") # Changed from Артикулът
    if product.organization_id != current_org.id: # Changed from item
        raise HTTPException(
            status_code=403,
            detail="Продуктът принадлежи на друга организация", # Changed from Артикулът
        )

    recipe_item = create_recipe_item(
        session=session, recipe_id=recipe_id, item_in=item_in
    )
    return recipe_item


@router.put("/{recipe_id}/items/{product_id}", response_model=RecipeItemPublic) # Changed item_id to product_id
def update_recipe_item_endpoint(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    recipe_id: uuid.UUID,
    product_id: uuid.UUID, # Changed from item_id
    item_in: RecipeItemUpdate,
) -> Any:
    """
    Update a recipe item. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Изисква се роля мениджър")

    recipe = get_recipe(
        session=session, recipe_id=recipe_id, organization_id=current_org.id
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецептата не е намерена")

    recipe_item = get_recipe_item(
        session=session, product_id=product_id, recipe_id=recipe_id # Changed item_id to product_id
    )
    if not recipe_item:
        raise HTTPException(status_code=404, detail="Компонентът не е намерен")

    recipe_item = update_recipe_item(
        session=session, db_item=recipe_item, item_in=item_in
    )
    return recipe_item


@router.delete("/{recipe_id}/items/{product_id}") # Changed item_id to product_id
def delete_recipe_item_endpoint(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    recipe_id: uuid.UUID,
    product_id: uuid.UUID, # Changed from item_id
) -> Message:
    """
    Delete a recipe item. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Изисква се роля мениджър")

    recipe = get_recipe(
        session=session, recipe_id=recipe_id, organization_id=current_org.id
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Рецептата не е намерена")

    recipe_item = get_recipe_item(
        session=session, product_id=product_id, recipe_id=recipe_id # Changed item_id to product_id
    )
    if not recipe_item:
        raise HTTPException(status_code=404, detail="Компонентът не е намерен")

    delete_recipe_item(session=session, db_item=recipe_item)
    return Message(message="Компонентът е изтрит успешно")
