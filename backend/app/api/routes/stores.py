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
    Store,
    StoreCreate,
    StorePublic,
    StoresPublic,
    StoreUpdate,
    has_role_or_higher,
)

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("/", response_model=StoresPublic)
def read_stores(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve stores for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(Store)
        .where(Store.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Store)
        .where(Store.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    stores = session.exec(statement).all()

    return StoresPublic(data=stores, count=count)


@router.get("/{id}", response_model=StorePublic)
def read_store(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get store by ID.
    """
    store = session.get(Store, id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if store.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return store


@router.post("/", response_model=StorePublic)
def create_store(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    store_in: StoreCreate,
) -> Any:
    """
    Create new store. Requires at least member role.
    """
    store = Store.model_validate(
        store_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


@router.put("/{id}", response_model=StorePublic)
def update_store(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    store_in: StoreUpdate,
) -> Any:
    """
    Update a store. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    store = session.get(Store, id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if store.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = store_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    store.sqlmodel_update(update_dict)
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


@router.delete("/{id}")
def delete_store(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete a store. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    store = session.get(Store, id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if store.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(store)
    session.commit()
    return Message(message="Store deleted successfully")

# TODO: consider to add a feature for getting low stock stores
