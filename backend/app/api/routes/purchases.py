import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
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
    Purchase,
    PurchaseCreate,
    PurchasePublic,
    PurchasesPublic,
    PurchaseUpdate,
    Store,
    Supplier,
    has_role_or_higher,
)
from app.utils import to_public

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.get("/", response_model=PurchasesPublic)
def read_purchases(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve purchases for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(Purchase)
        .where(Purchase.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Purchase)
        .options(selectinload(Purchase.supplier), selectinload(Purchase.store))
        .where(Purchase.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    purchases = session.exec(statement).all()
    purchases = to_public(
        purchases,
        schema=PurchasePublic,
        extra_fields={
            "supplier_name": lambda p: p.supplier.name,
            "store_name": lambda p: p.store.name,
        },
    )
    return PurchasesPublic(data=purchases, count=count)


@router.get("/{id}", response_model=PurchasePublic)
def read_purchase(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get purchase by ID.
    """
    purchase = session.get(Purchase, id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    if purchase.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return purchase


@router.post("/", response_model=PurchasePublic)
def create_purchase(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    purchase_in: PurchaseCreate,
) -> Any:
    """
    Create new purchase. Requires at least member role.
    """
    supplier = session.get(Supplier, purchase_in.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    if supplier.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Supplier belongs to another organization")

    store = session.get(Store, purchase_in.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if store.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Store belongs to another organization")

    purchase = Purchase.model_validate(
        purchase_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(purchase)
    session.commit()
    session.refresh(purchase)
    return to_public(
        purchase,
        schema=PurchasePublic,
        extra_fields={
            "supplier_name": lambda p: p.supplier.name,
            "store_name": lambda p: p.store.name,
        },
    )


@router.put("/{id}", response_model=PurchasePublic)
def update_purchase(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    purchase_in: PurchaseUpdate,
) -> Any:
    """
    Update a purchase. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    purchase = session.get(Purchase, id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    if purchase.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if purchase_in.supplier_id is not None:
        supplier = session.get(Supplier, purchase_in.supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        if supplier.organization_id != current_org.id:
            raise HTTPException(status_code=403, detail="Supplier belongs to another organization")

    if purchase_in.store_id is not None:
        store = session.get(Store, purchase_in.store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        if store.organization_id != current_org.id:
            raise HTTPException(status_code=403, detail="Store belongs to another organization")

    update_dict = purchase_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    purchase.sqlmodel_update(update_dict)
    session.add(purchase)
    session.commit()
    session.refresh(purchase)
    return to_public(
        purchase,
        schema=PurchasePublic,
        extra_fields={
            "supplier_name": lambda p: p.supplier.name,
            "store_name": lambda p: p.store.name,
        },
    )


@router.delete("/{id}")
def delete_purchase(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete a purchase. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    purchase = session.get(Purchase, id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    if purchase.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(purchase)
    session.commit()
    return Message(message="Purchase deleted successfully")
