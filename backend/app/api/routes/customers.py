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
    Customer,
    CustomerCreate,
    CustomerPublic,
    CustomersPublic,
    CustomerType,
    CustomerUpdate,
    Message,
    OrganizationRole,
    has_role_or_higher,
)

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/", response_model=CustomersPublic)
def read_customers(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve customers for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(Customer)
        .where(Customer.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Customer)
        .options(selectinload(Customer.customer_type))
        .where(Customer.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    customers = session.exec(statement).all()
    customers = [
        CustomerPublic(
            **{
                **customer.model_dump(),
                "customer_type_name": customer.customer_type.name,
            }
        )
        for customer in customers
    ]
    return CustomersPublic(data=customers, count=count)


@router.get("/{id}", response_model=CustomerPublic)
def read_customer(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get customer by ID.
    """
    customer = session.get(Customer, id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if customer.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return customer


@router.post("/", response_model=CustomerPublic)
def create_customer(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    customer_in: CustomerCreate,
) -> Any:
    """
    Create new customer. Requires at least member role.
    """
    customer_type = session.get(CustomerType, customer_in.customer_type_id)
    if not customer_type:
        raise HTTPException(status_code=404, detail="Customer type not found")
    if customer_type.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Customer type belongs to another organization")

    customer = Customer.model_validate(
        customer_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.put("/{id}", response_model=CustomerPublic)
def update_customer(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    customer_in: CustomerUpdate,
) -> Any:
    """
    Update a customer. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    customer = session.get(Customer, id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if customer.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if customer_in.customer_type_id is not None:
        customer_type = session.get(CustomerType, customer_in.customer_type_id)
        if not customer_type:
            raise HTTPException(status_code=404, detail="Customer type not found")
        if customer_type.organization_id != current_org.id:
            raise HTTPException(status_code=403, detail="Customer type belongs to another organization")

    update_dict = customer_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    customer.sqlmodel_update(update_dict)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.delete("/{id}")
def delete_customer(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete a customer. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    customer = session.get(Customer, id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if customer.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(customer)
    session.commit()
    return Message(message="Customer deleted successfully")
