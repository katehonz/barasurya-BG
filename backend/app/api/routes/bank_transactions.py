"""
API routes за банкови транзакции.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.api.deps import get_current_organization, get_db
from app.models import (
    BankTransaction,
    BankTransactionCreate,
    BankTransactionUpdate,
    BankTransactionPublic,
    BankTransactionsPublic,
    BankAccount,
    Organization,
)
from app.utils import utcnow

router = APIRouter(prefix="/bank-transactions", tags=["bank-transactions"])


@router.get("/", response_model=BankTransactionsPublic)
def list_bank_transactions(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    skip: int = 0,
    limit: int = 100,
    bank_account_id: uuid.UUID | None = None,
    is_processed: bool | None = None,
    is_credit: bool | None = None,
) -> Any:
    """Списък банкови транзакции."""
    query = select(BankTransaction).where(
        BankTransaction.organization_id == current_organization.id
    )

    if bank_account_id:
        query = query.where(BankTransaction.bank_account_id == bank_account_id)
    if is_processed is not None:
        query = query.where(BankTransaction.is_processed == is_processed)
    if is_credit is not None:
        query = query.where(BankTransaction.is_credit == is_credit)

    query = query.order_by(BankTransaction.booking_date.desc())

    count_query = select(func.count()).select_from(query.subquery())
    count = session.exec(count_query).one()

    transactions = session.exec(query.offset(skip).limit(limit)).all()

    return BankTransactionsPublic(data=transactions, count=count)


@router.get("/{transaction_id}", response_model=BankTransactionPublic)
def get_bank_transaction(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    transaction_id: uuid.UUID,
) -> Any:
    """Получаване на банкова транзакция по ID."""
    transaction = session.get(BankTransaction, transaction_id)
    if not transaction or transaction.organization_id != current_organization.id:
        raise HTTPException(status_code=404, detail="Транзакцията не е намерена")
    return transaction


@router.post("/", response_model=BankTransactionPublic)
def create_bank_transaction(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    transaction_in: BankTransactionCreate,
) -> Any:
    """Създаване на нова банкова транзакция."""
    # Verify bank account exists and belongs to organization
    bank_account = session.get(BankAccount, transaction_in.bank_account_id)
    if not bank_account or bank_account.organization_id != current_organization.id:
        raise HTTPException(status_code=404, detail="Банковата сметка не е намерена")

    transaction = BankTransaction(
        **transaction_in.model_dump(),
        organization_id=current_organization.id,
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.put("/{transaction_id}", response_model=BankTransactionPublic)
def update_bank_transaction(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    transaction_id: uuid.UUID,
    transaction_in: BankTransactionUpdate,
) -> Any:
    """Актуализация на банкова транзакция."""
    transaction = session.get(BankTransaction, transaction_id)
    if not transaction or transaction.organization_id != current_organization.id:
        raise HTTPException(status_code=404, detail="Транзакцията не е намерена")

    update_data = transaction_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    transaction.date_updated = utcnow()
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}")
def delete_bank_transaction(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    transaction_id: uuid.UUID,
) -> Any:
    """Изтриване на банкова транзакция."""
    transaction = session.get(BankTransaction, transaction_id)
    if not transaction or transaction.organization_id != current_organization.id:
        raise HTTPException(status_code=404, detail="Транзакцията не е намерена")

    session.delete(transaction)
    session.commit()
    return {"message": "Транзакцията е изтрита успешно"}


@router.post("/{transaction_id}/process", response_model=BankTransactionPublic)
def process_bank_transaction(
    *,
    session: Session = Depends(get_db),
    current_organization: Organization = Depends(get_current_organization),
    transaction_id: uuid.UUID,
    journal_entry_id: uuid.UUID | None = None,
) -> Any:
    """Маркиране на транзакция като обработена."""
    transaction = session.get(BankTransaction, transaction_id)
    if not transaction or transaction.organization_id != current_organization.id:
        raise HTTPException(status_code=404, detail="Транзакцията не е намерена")

    transaction.is_processed = True
    transaction.processed_at = utcnow()
    if journal_entry_id:
        transaction.journal_entry_id = journal_entry_id

    transaction.date_updated = utcnow()
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction
