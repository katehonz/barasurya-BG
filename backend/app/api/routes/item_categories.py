import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import (
    CurrentMembership,
    CurrentOrganization,
    CurrentUser,
    RequireManager,
    SessionDep,
)
from app.models import (
    BaseModelUpdate,
    ItemCategoriesPublic,
    ItemCategory,
    ItemCategoryCreate,
    ItemCategoryPublic,
    ItemCategoryUpdate,
    Message,
    OrganizationRole,
    has_role_or_higher,
)

router = APIRouter(prefix="/item_categories", tags=["item_categories"])


@router.get("/", response_model=ItemCategoriesPublic)
def read_item_categories(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve item categories for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(ItemCategory)
        .where(ItemCategory.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(ItemCategory)
        .where(ItemCategory.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    item_categories = session.exec(statement).all()

    return ItemCategoriesPublic(data=item_categories, count=count)


@router.get("/{id}", response_model=ItemCategoryPublic)
def read_item_category(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get item category by ID.
    """
    item_category = session.get(ItemCategory, id)
    if not item_category:
        raise HTTPException(status_code=404, detail="Item category not found")
    if item_category.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item_category


@router.post("/", response_model=ItemCategoryPublic)
def create_item_category(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    item_category_in: ItemCategoryCreate,
) -> Any:
    """
    Create new item category. Requires at least member role.
    """
    item_category = ItemCategory.model_validate(
        item_category_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(item_category)
    session.commit()
    session.refresh(item_category)
    return item_category


@router.put("/{id}", response_model=ItemCategoryPublic)
def update_item_category(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    item_category_in: ItemCategoryUpdate,
) -> Any:
    """
    Update an item category. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    item_category = session.get(ItemCategory, id)
    if not item_category:
        raise HTTPException(status_code=404, detail="Item category not found")
    if item_category.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = item_category_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    item_category.sqlmodel_update(update_dict)
    session.add(item_category)
    session.commit()
    session.refresh(item_category)
    return item_category


@router.delete("/{id}")
def delete_item_category(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete an item category. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    item_category = session.get(ItemCategory, id)
    if not item_category:
        raise HTTPException(status_code=404, detail="Item category not found")
    if item_category.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(item_category)
    session.commit()
    return Message(message="Item category deleted successfully")
