import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    BaseModelUpdate,
    Customer,
    Message,
    Sale,
    SaleCreate,
    SalePublic,
    SalesPublic,
    SaleUpdate,
    Store,
)
from app.utils import to_public

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=SalesPublic)
def read_sales(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve sale types.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Sale)
        count = session.exec(count_statement).one()
        statement = (
            select(Sale)
            .options(selectinload(Sale.customer), selectinload(Sale.store))
            .offset(skip)
            .limit(limit)
        )
        sales = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Sale)
            .where(Sale.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Sale)
            .options(selectinload(Sale.customer), selectinload(Sale.store))
            .where(Sale.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        sales = session.exec(statement).all()
    sales = to_public(
        sales,
        schema=SalePublic,
        extra_fields={
            "customer_name": lambda p: p.customer.name,
            "store_name": lambda p: p.store.name,
        },
    )
    return SalesPublic(data=sales, count=count)


@router.get("/{id}", response_model=SalePublic)
def read_sale(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get sale type by ID.
    """
    sale = session.get(Sale, id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if not current_user.is_superuser and (sale.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return sale


@router.post("/", response_model=SalePublic)
def create_sale(
    *, session: SessionDep, current_user: CurrentUser, sale_in: SaleCreate
) -> Any:
    """
    Create new sale type.
    """
    customer = session.get(Customer, sale_in.customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    store = session.get(Store, sale_in.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    sale = Sale.model_validate(sale_in, update={"owner_id": current_user.id})
    session.add(sale)
    session.commit()
    session.refresh(sale)
    return to_public(
        sale,
        schema=SalePublic,
        extra_fields={
            "customer_name": lambda p: p.customer.name,
            "store_name": lambda p: p.store.name,
        },
    )


@router.put("/{id}", response_model=SalePublic)
def update_sale(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    sale_in: SaleUpdate,
) -> Any:
    """
    Update a sale.
    """
    sale = session.get(Sale, id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if not current_user.is_superuser and (sale.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if sale_in.customer_id is not None:
        customer = session.get(Customer, sale_in.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
    if sale_in.store_id is not None:
        store = session.get(Store, sale_in.store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
    update_dict = sale_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    sale.sqlmodel_update(update_dict)
    session.add(sale)
    session.commit()
    session.refresh(sale)
    return to_public(
        sale,
        schema=SalePublic,
        extra_fields={
            "customer_name": lambda p: p.customer.name,
            "store_name": lambda p: p.store.name,
        },
    )


@router.delete("/{id}")
def delete_sale(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a sale.
    """
    sale = session.get(Sale, id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if not current_user.is_superuser and (sale.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(sale)
    session.commit()
    return Message(message="Sale deleted successfully")


# TODO: consider to add a feature for getting low stock sales
