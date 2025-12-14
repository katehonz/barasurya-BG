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
    CustomerType,
    CustomerTypeCreate,
    CustomerTypePublic,
    CustomerTypesPublic,
    CustomerTypeUpdate,
    Message,
    OrganizationRole,
    has_role_or_higher,
)

router = APIRouter(prefix="/customer_types", tags=["customer_types"])


@router.get("/", response_model=CustomerTypesPublic)
def read_customer_types(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve customer types for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(CustomerType)
        .where(CustomerType.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(CustomerType)
        .where(CustomerType.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    customer_types = session.exec(statement).all()

    return CustomerTypesPublic(data=customer_types, count=count)


@router.get("/{id}", response_model=CustomerTypePublic)
def read_customer_type(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get customer type by ID.
    """
    customer_type = session.get(CustomerType, id)
    if not customer_type:
        raise HTTPException(status_code=404, detail="CustomerType not found")
    if customer_type.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return customer_type


@router.post("/", response_model=CustomerTypePublic)
def create_customer_type(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    customer_type_in: CustomerTypeCreate,
) -> Any:
    """
    Create new customer type. Requires at least member role.
    """
    customer_type = CustomerType.model_validate(
        customer_type_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(customer_type)
    session.commit()
    session.refresh(customer_type)
    return customer_type


@router.put("/{id}", response_model=CustomerTypePublic)
def update_customer_type(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    customer_type_in: CustomerTypeUpdate,
) -> Any:
    """
    Update a customer type. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    customer_type = session.get(CustomerType, id)
    if not customer_type:
        raise HTTPException(status_code=404, detail="CustomerType not found")
    if customer_type.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = customer_type_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    customer_type.sqlmodel_update(update_dict)
    session.add(customer_type)
    session.commit()
    session.refresh(customer_type)
    return customer_type


@router.delete("/{id}")
def delete_customer_type(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete a customer type. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    customer_type = session.get(CustomerType, id)
    if not customer_type:
        raise HTTPException(status_code=404, detail="CustomerType not found")
    if customer_type.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(customer_type)
    session.commit()
    return Message(message="CustomerType deleted successfully")
