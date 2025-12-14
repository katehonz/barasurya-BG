import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    BaseModelUpdate,
    Message,
    Purchase,
    PurchaseCreate,
    PurchasePublic,
    PurchasesPublic,
    PurchaseUpdate,
    Store,
    Supplier,
)
from app.utils import to_public

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.get("/", response_model=PurchasesPublic)
def read_purchases(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve purchase types.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Purchase)
        count = session.exec(count_statement).one()
        statement = (
            select(Purchase)
            .options(selectinload(Purchase.supplier), selectinload(Purchase.store))
            .offset(skip)
            .limit(limit)
        )
        purchases = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Purchase)
            .where(Purchase.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Purchase)
            .options(selectinload(Purchase.supplier), selectinload(Purchase.store))
            .where(Purchase.owner_id == current_user.id)
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
def read_purchase(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get purchase type by ID.
    """
    purchase = session.get(Purchase, id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    if not current_user.is_superuser and (purchase.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return purchase


@router.post("/", response_model=PurchasePublic)
def create_purchase(
    *, session: SessionDep, current_user: CurrentUser, purchase_in: PurchaseCreate
) -> Any:
    """
    Create new purchase type.
    """
    supplier = session.get(Supplier, purchase_in.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    store = session.get(Store, purchase_in.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    purchase = Purchase.model_validate(
        purchase_in, update={"owner_id": current_user.id}
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
    current_user: CurrentUser,
    id: uuid.UUID,
    purchase_in: PurchaseUpdate,
) -> Any:
    """
    Update a purchase.
    """
    purchase = session.get(Purchase, id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    if not current_user.is_superuser and (purchase.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if purchase_in.supplier_id is not None:
        supplier = session.get(Supplier, purchase_in.supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
    if purchase_in.store_id is not None:
        store = session.get(Store, purchase_in.store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
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
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a purchase.
    """
    purchase = session.get(Purchase, id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    if not current_user.is_superuser and (purchase.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(purchase)
    session.commit()
    return Message(message="Purchase deleted successfully")


# TODO: consider to add a feature for getting low stock purchases
