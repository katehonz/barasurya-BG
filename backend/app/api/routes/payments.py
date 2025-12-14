
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
    Payment,
    PaymentCreate,
    PaymentPublic,
    PaymentsPublic,
    PaymentUpdate,
    Account,
    has_role_or_higher,
)
from app.services.journal import JournalService
from app.utils import to_public

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", response_model=PaymentsPublic)
def read_payments(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve payments for the current organization.
    """
    count_statement = (
        select(func.count())
        .select_from(Payment)
        .where(Payment.organization_id == current_org.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Payment)
        .options(selectinload(Payment.account))
        .where(Payment.organization_id == current_org.id)
        .offset(skip)
        .limit(limit)
    )
    payments = session.exec(statement).all()
    return PaymentsPublic(data=to_public(payments, PaymentPublic), count=count)


@router.post("/", response_model=PaymentPublic)
def create_payment(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    payment_in: PaymentCreate,
) -> Any:
    """
    Create new payment.
    """
    account = session.get(Account, payment_in.account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.organization_id != current_org.id:
        raise HTTPException(status_code=403, detail="Account belongs to another organization")

    payment = Payment.model_validate(
        payment_in,
        update={
            "organization_id": current_org.id,
            "created_by_id": current_user.id,
        },
    )
    session.add(payment)
    session.commit()
    session.refresh(payment)

    journal_service = JournalService(session, current_user, current_org)
    journal_service.create_journal_entry_for_payment(payment)

    return to_public(payment, PaymentPublic)
