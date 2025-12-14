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
    ItemUnit,
    ItemUnitCreate,
    ItemUnitPublic,
    ItemUnitsPublic,
    ItemUnitUpdate,
    Message,
    OrganizationRole,
    has_role_or_higher,
)

router = APIRouter(prefix="/item_units", tags=["item_units"])


@router.get("/", response_model=ItemUnitsPublic)
def read_item_units(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve item units for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(ItemUnit)
        .where(ItemUnit.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(ItemUnit)
        .where(ItemUnit.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    item_units = session.exec(statement).all()

    return ItemUnitsPublic(data=item_units, count=count)


@router.get("/{id}", response_model=ItemUnitPublic)
def read_item_unit(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get item unit by ID.
    """
    item_unit = session.get(ItemUnit, id)
    if not item_unit:
        raise HTTPException(status_code=404, detail="Item unit not found")
    if item_unit.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return item_unit


@router.post("/", response_model=ItemUnitPublic)
def create_item_unit(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    item_unit_in: ItemUnitCreate,
) -> Any:
    """
    Create new item unit. Requires at least member role.
    """
    item_unit = ItemUnit.model_validate(
        item_unit_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(item_unit)
    session.commit()
    session.refresh(item_unit)
    return item_unit


@router.put("/{id}", response_model=ItemUnitPublic)
def update_item_unit(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    item_unit_in: ItemUnitUpdate,
) -> Any:
    """
    Update an item unit. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    item_unit = session.get(ItemUnit, id)
    if not item_unit:
        raise HTTPException(status_code=404, detail="Item unit not found")
    if item_unit.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = item_unit_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    item_unit.sqlmodel_update(update_dict)
    session.add(item_unit)
    session.commit()
    session.refresh(item_unit)
    return item_unit


@router.delete("/{id}")
def delete_item_unit(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete an item unit. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    item_unit = session.get(ItemUnit, id)
    if not item_unit:
        raise HTTPException(status_code=404, detail="Item unit not found")
    if item_unit.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(item_unit)
    session.commit()
    return Message(message="Item unit deleted successfully")
