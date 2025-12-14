"""
API routes за банкови сметки.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.api.deps import get_current_organization, get_db, CurrentUser
from app.models import (
    BankAccount,
    BankAccountCreate,
    BankAccountUpdate,
    BankAccountPublic,
    BankAccountsPublic,
    Organization,
)
from app.utils import utcnow

router = APIRouter(prefix="/bank-accounts", tags=["bank-accounts"])


@router.get("/", response_model=BankAccountsPublic)
def list_bank_accounts(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
) -> Any:
    """Списък банкови сметки."""
    query = select(BankAccount).where(
        BankAccount.organization_id == current_organization.id
    )

    if is_active is not None:
        query = query.where(BankAccount.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    count = session.exec(count_query).one()

    accounts = session.exec(query.offset(skip).limit(limit)).all()

    return BankAccountsPublic(data=accounts, count=count)


@router.get("/{account_id}", response_model=BankAccountPublic)
def get_bank_account(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    account_id: uuid.UUID,
) -> Any:
    """Получаване на банкова сметка по ID."""
    account = session.get(BankAccount, account_id)
    if not account or account.organization_id != current_organization.id:
        raise HTTPException(status_code=404, detail="Банковата сметка не е намерена")
    return account


@router.post("/", response_model=BankAccountPublic)
def create_bank_account(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    account_in: BankAccountCreate,
) -> Any:
    """Създаване на нова банкова сметка."""
    # Check for duplicate IBAN
    existing = session.exec(
        select(BankAccount).where(
            BankAccount.organization_id == current_organization.id,
            BankAccount.iban == account_in.iban
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Вече съществува сметка с този IBAN")

    account = BankAccount(
        **account_in.model_dump(),
        organization_id=current_organization.id,
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@router.put("/{account_id}", response_model=BankAccountPublic)
def update_bank_account(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    account_id: uuid.UUID,
    account_in: BankAccountUpdate,
) -> Any:
    """Актуализация на банкова сметка."""
    account = session.get(BankAccount, account_id)
    if not account or account.organization_id != current_organization.id:
        raise HTTPException(status_code=404, detail="Банковата сметка не е намерена")

    update_data = account_in.model_dump(exclude_unset=True)

    # Check for duplicate IBAN if changing
    if "iban" in update_data and update_data["iban"] != account.iban:
        existing = session.exec(
            select(BankAccount).where(
                BankAccount.organization_id == current_organization.id,
                BankAccount.iban == update_data["iban"],
                BankAccount.id != account_id
            )
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Вече съществува сметка с този IBAN")

    for field, value in update_data.items():
        setattr(account, field, value)

    account.date_updated = utcnow()
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


@router.delete("/{account_id}")
def delete_bank_account(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    account_id: uuid.UUID,
) -> Any:
    """Изтриване на банкова сметка."""
    account = session.get(BankAccount, account_id)
    if not account or account.organization_id != current_organization.id:
        raise HTTPException(status_code=404, detail="Банковата сметка не е намерена")

    session.delete(account)
    session.commit()
    return {"message": "Банковата сметка е изтрита успешно"}
