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
    Message,
    OrganizationRole,
    StockLevel,
    StockLevelCreate,
    StockLevelPublic,
    StockLevelsPublic,
    StockLevelUpdate,
    has_role_or_higher,
)

router = APIRouter(prefix="/stock_levels", tags=["stock_levels"])


@router.get("/", response_model=StockLevelsPublic)
def read_stock_levels(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve stock levels for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(StockLevel)
        .where(StockLevel.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(StockLevel)
        .where(StockLevel.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    stock_levels = session.exec(statement).all()
    return StockLevelsPublic(data=stock_levels, count=count)


@router.get("/{id}", response_model=StockLevelPublic)
def read_stock_level(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get stock level by ID.
    """
    stock_level = session.get(StockLevel, id)
    if not stock_level:
        raise HTTPException(status_code=404, detail="Stock level not found")
    if stock_level.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return stock_level


@router.post("/", response_model=StockLevelPublic)
def create_stock_level(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    stock_level_in: StockLevelCreate,
) -> Any:
    """
    Create new stock level. Requires at least member role.
    """
    stock_level = StockLevel.model_validate(
        stock_level_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(stock_level)
    session.commit()
    session.refresh(stock_level)
    return stock_level


@router.put("/{id}", response_model=StockLevelPublic)
def update_stock_level(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    stock_level_in: StockLevelUpdate,
) -> Any:
    """
    Update a stock level. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    stock_level = session.get(StockLevel, id)
    if not stock_level:
        raise HTTPException(status_code=404, detail="Stock level not found")
    if stock_level.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = stock_level_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    stock_level.sqlmodel_update(update_dict)
    session.add(stock_level)
    session.commit()
    session.refresh(stock_level)
    return stock_level


@router.delete("/{id}")
def delete_stock_level(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete a stock level. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    stock_level = session.get(StockLevel, id)
    if not stock_level:
        raise HTTPException(status_code=404, detail="Stock level not found")
    if stock_level.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(stock_level)
    session.commit()
    return Message(message="Stock level deleted successfully")
