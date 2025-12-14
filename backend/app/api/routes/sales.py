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
    Sale,
    SaleCreate,
    SalePublic,
    SalesPublic,
    SaleUpdate,
    Store,
    Contraagent,
    has_role_or_higher,
)
from app.services.journal import JournalService
from app.utils import to_public

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=SalesPublic)
def read_sales(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve sales for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(Sale)
        .where(Sale.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Sale)
        .options(selectinload(Sale.contraagent), selectinload(Sale.store))
        .where(Sale.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    sales = session.exec(statement).all()
    sales = to_public(
        sales,
        schema=SalePublic,
        extra_fields={
            "contraagent_name": lambda p: p.contraagent.name,
            "store_name": lambda p: p.store.name,
        },
    )
    return SalesPublic(data=sales, count=count)


@router.get("/{id}", response_model=SalePublic)
def read_sale(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get sale by ID.
    """
    sale = session.get(Sale, id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if sale.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return sale


@router.post("/", response_model=SalePublic)
def create_sale(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    sale_in: SaleCreate,
) -> Any:
    """
    Create new sale. Requires at least member role.
    """
    contraagent = session.get(Contraagent, sale_in.contraagent_id)
    if not contraagent:
        raise HTTPException(status_code=404, detail="Contraagent not found")
    if contraagent.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Contraagent belongs to another organization")
    if not contraagent.is_customer:
        raise HTTPException(status_code=403, detail="Contraagent is not a customer")

    store = session.get(Store, sale_in.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if store.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Store belongs to another organization")

    sale = Sale.model_validate(
        sale_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(sale)
    session.commit()
    session.refresh(sale)

    journal_service = JournalService(session, current_user, current_org)
    journal_service.create_journal_entry_for_sale(sale)

    return to_public(
        sale,
        schema=SalePublic,
        extra_fields={
            "contraagent_name": lambda p: p.contraagent.name,
            "store_name": lambda p: p.store.name,
        },
    )


@router.put("/{id}", response_model=SalePublic)
def update_sale(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    sale_in: SaleUpdate,
) -> Any:
    """
    Update a sale. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    sale = session.get(Sale, id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if sale.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if sale_in.contraagent_id is not None:
        contraagent = session.get(Contraagent, sale_in.contraagent_id)
        if not contraagent:
            raise HTTPException(status_code=404, detail="Contraagent not found")
        if contraagent.organization_id != current_org.id:
            raise HTTPException(status_code=403, detail="Contraagent belongs to another organization")
        if not contraagent.is_customer:
            raise HTTPException(status_code=403, detail="Contraagent is not a customer")

    if sale_in.store_id is not None:
        store = session.get(Store, sale_in.store_id)
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
        if store.organization_id != current_org.id:
            raise HTTPException(status_code=403, detail="Store belongs to another organization")

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
            "contraagent_name": lambda p: p.contraagent.name,
            "store_name": lambda p: p.store.name,
        },
    )


@router.delete("/{id}")
def delete_sale(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete a sale. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    sale = session.get(Sale, id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if sale.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(sale)
    session.commit()
    return Message(message="Sale deleted successfully")
