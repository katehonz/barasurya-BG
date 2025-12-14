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
    Supplier,
    SupplierCreate,
    SupplierPublic,
    SuppliersPublic,
    SupplierUpdate,
    has_role_or_higher,
)

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("/", response_model=SuppliersPublic)
def read_suppliers(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve suppliers for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(Supplier)
        .where(Supplier.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Supplier)
        .where(Supplier.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    suppliers = session.exec(statement).all()

    return SuppliersPublic(data=suppliers, count=count)


@router.get("/{id}", response_model=SupplierPublic)
def read_supplier(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get supplier by ID.
    """
    supplier = session.get(Supplier, id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    if supplier.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return supplier


@router.post("/", response_model=SupplierPublic)
def create_supplier(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    supplier_in: SupplierCreate,
) -> Any:
    """
    Create new supplier. Requires at least member role.
    """
    supplier = Supplier.model_validate(
        supplier_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    return supplier


@router.put("/{id}", response_model=SupplierPublic)
def update_supplier(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    supplier_in: SupplierUpdate,
) -> Any:
    """
    Update a supplier. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    supplier = session.get(Supplier, id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    if supplier.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = supplier_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    supplier.sqlmodel_update(update_dict)
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    return supplier


@router.delete("/{id}")
def delete_supplier(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete a supplier. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    supplier = session.get(Supplier, id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    if supplier.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(supplier)
    session.commit()
    return Message(message="Supplier deleted successfully")
