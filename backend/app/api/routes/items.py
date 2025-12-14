import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import and_, func, select

from app.api.deps import (
    CurrentMembership,
    CurrentOrganization,
    CurrentUser,
    RequireManager,
    SessionDep,
)
from app.models import (
    BaseModelUpdate,
    Item,
    ItemCategory,
    ItemCreate,
    ItemPublic,
    ItemsPublic,
    ItemUnit,
    ItemUpdate,
    Message,
    OrganizationRole,
    StockLevel,
    Store,
    has_role_or_higher,
)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve items for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(Item)
        .where(Item.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Item)
        .options(selectinload(Item.item_category), selectinload(Item.item_unit))
        .where(Item.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    items = session.exec(statement).all()
    items_public = []
    for item in items:
        stock_statement = select(func.sum(StockLevel.quantity)).where(
            StockLevel.item_id == item.id
        )
        stock = session.exec(stock_statement).one_or_none() or 0
        item_public = ItemPublic(
            **{
                **item.model_dump(),
                "item_category_name": item.item_category.name,
                "item_unit_name": item.item_unit.name,
                "stock": stock,
            }
        )
        items_public.append(item_public)
    return ItemsPublic(data=items_public, count=count)


@router.get("/{id}", response_model=ItemPublic)
def read_item(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get item by ID.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    stock_statement = select(func.sum(StockLevel.quantity)).where(
        StockLevel.item_id == item.id
    )
    stock = session.exec(stock_statement).one_or_none() or 0
    item_public = ItemPublic(
        **{
            **item.model_dump(),
            "item_category_name": item.item_category.name,
            "item_unit_name": item.item_unit.name,
            "stock": stock,
        }
    )
    return item_public


@router.post("/", response_model=ItemPublic)
def create_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    item_in: ItemCreate,
) -> Any:
    """
    Create new item. Requires at least member role.
    """
    item_category = session.get(ItemCategory, item_in.item_category_id)
    if not item_category:
        raise HTTPException(status_code=404, detail="Item category not found")
    if item_category.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Item category belongs to another organization")

    item_unit = session.get(ItemUnit, item_in.item_unit_id)
    if not item_unit:
        raise HTTPException(status_code=404, detail="Item unit not found")
    if item_unit.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Item unit belongs to another organization")

    item = Item.model_validate(
        item_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(item)
    session.commit()
    session.refresh(item)

    # Create a stock level for each store
    stores = session.exec(
        select(Store).where(Store.organization_id == current_org.id)
    ).all()
    for store in stores:
        stock_level = StockLevel(
            item_id=item.id,
            store_id=store.id,
            quantity=0,
            organization_id=current_org.id,
            created_by_id=current_user.id,
        )
        session.add(stock_level)
    session.commit()

    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if item_in.item_category_id is not None:
        item_category = session.get(ItemCategory, item_in.item_category_id)
        if not item_category:
            raise HTTPException(status_code=404, detail="Item category not found")
        if item_category.organization_id != current_org.id:
            raise HTTPException(status_code=403, detail="Item category belongs to another organization")

    if item_in.item_unit_id is not None:
        item_unit = session.get(ItemUnit, item_in.item_unit_id)
        if not item_unit:
            raise HTTPException(status_code=404, detail="Item unit not found")
        if item_unit.organization_id != current_org.id:
            raise HTTPException(status_code=403, detail="Item unit belongs to another organization")

    update_dict = item_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{id}")
def delete_item(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete an item. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")


@router.get("/low_stock/", response_model=ItemsPublic)
def read_low_stock_items(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve low stock items for the current organization.
    """
    subquery = (
        select(
            StockLevel.item_id,
            func.sum(StockLevel.quantity).label("total_stock"),
        )
        .where(StockLevel.organization_id == current_org.id)
        .group_by(StockLevel.item_id)
        .subquery()
    )

    count_statement = (
        select(func.count())
        .select_from(Item)
        .join(subquery, subquery.c.item_id == Item.id)
        .where(
            and_(
                Item.organization_id == current_org.id,
                subquery.c.total_stock <= Item.stock_minimum,
            )
        )
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Item)
        .join(subquery, subquery.c.item_id == Item.id)
        .where(
            and_(
                Item.organization_id == current_org.id,
                subquery.c.total_stock <= Item.stock_minimum,
            )
        )
        .offset(skip)
        .limit(limit)
    )
    items = session.exec(statement).all()

    return ItemsPublic(data=items, count=count)


@router.put("/{id}/activate", response_model=ItemPublic)
def activate_item(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Activate an item. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    item.is_active = True
    item.sqlmodel_update(BaseModelUpdate().model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{id}/deactivate", response_model=ItemPublic)
def deactivate_item(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Deactivate an item. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    item.is_active = False
    item.sqlmodel_update(BaseModelUpdate().model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
