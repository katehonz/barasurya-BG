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
    Account,
    AccountCreate,
    AccountPublic,
    AccountsPublic,
    AccountUpdate,
    BaseModelUpdate,
    Message,
    OrganizationRole,
    has_role_or_higher,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=AccountsPublic)
def read_accounts(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve accounts for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(Account)
        .where(Account.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Account)
        .where(Account.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    accounts = session.exec(statement).all()

    return AccountsPublic(data=accounts, count=count)


@router.get("/{id}", response_model=AccountPublic)
def read_account(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get account by ID.
    """
    account = session.get(Account, id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return account


@router.post("/", response_model=AccountPublic)
def create_account(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    account_in: AccountCreate,
) -> Any:
    """
    Create new account. Requires at least member role.
    """
    account = Account.model_validate(
        account_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@router.put("/{id}", response_model=AccountPublic)
def update_account(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    account_in: AccountUpdate,
) -> Any:
    """
    Update an account. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    account = session.get(Account, id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_dict = account_in.model_dump(exclude_unset=True)
    update_dict.update(BaseModelUpdate().model_dump())
    account.sqlmodel_update(update_dict)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@router.delete("/{id}")
def delete_account(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Delete an account. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    account = session.get(Account, id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    session.delete(account)
    session.commit()
    return Message(message="Account deleted successfully")
