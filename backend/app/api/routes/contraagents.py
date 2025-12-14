import uuid
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import (
    CurrentMembership,
    CurrentOrganization,
    CurrentUser,
    RequireManager,
    SessionDep,
)
from app.models import (
    Contraagent,
    ContraagentBankAccount,
    ContraagentBankAccountCreate,
    ContraagentBankAccountPublic,
    ContraagentBankAccountsPublic,
    ContraagentBankAccountUpdate,
    ContraagentCreate,
    ContraagentPublic,
    ContraagentsPublic,
    ContraagentUpdate,
    Message,
    OrganizationRole,
    has_role_or_higher,
)
from app.services.contraagent_service import ContraagentService, VIESValidator
from app.services.opening_balances_service import OpeningBalancesService

router = APIRouter(prefix="/contraagents", tags=["contraagents"])


# Contraagent endpoints
@router.get("/", response_model=ContraagentsPublic)
async def read_contraagents(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_customer: Optional[bool] = Query(None, description="Filter by customer status"),
    is_supplier: Optional[bool] = Query(None, description="Filter by supplier status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
) -> Any:
    """
    Retrieve contraagents for the current organization.
    """
    contraagents, count = await ContraagentService.get_contraagents(
        session=session,
        organization_id=current_org.id,
        skip=skip,
        limit=limit,
        search=search,
        is_customer=is_customer,
        is_supplier=is_supplier,
        is_active=is_active,
    )

    # Load related data for public response
    contraagents_public = []
    for contraagent in contraagents:
        # Load related data
        await session.refresh(contraagent, ["accounting_account"])

        accounting_account_name = None
        if contraagent.accounting_account:
            accounting_account_name = contraagent.accounting_account.name

        contraagents_public.append(
            ContraagentPublic(
                **contraagent.model_dump(),
                accounting_account_name=accounting_account_name,
            )
        )

    return ContraagentsPublic(data=contraagents_public, count=count)


@router.get("/{id}", response_model=ContraagentPublic)
async def read_contraagent(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get contraagent by ID.
    """
    contraagent = await ContraagentService.get_contraagent_by_id(
        session, current_org.id, id
    )
    if not contraagent:
        raise HTTPException(status_code=404, detail="Contraagent not found")

    # Load related data
    await session.refresh(contraagent, ["accounting_account"])

    accounting_account_name = None
    if contraagent.accounting_account:
        accounting_account_name = contraagent.accounting_account.name

    return ContraagentPublic(
        **contraagent.model_dump(),
        accounting_account_name=accounting_account_name,
    )


@router.post("/", response_model=ContraagentPublic)
async def create_contraagent(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    contraagent_in: ContraagentCreate,
    validate_vat: bool = Query(True, description="Validate VAT number using VIES"),
) -> Any:
    """
    Create new contraagent. Requires at least member role.
    """
    contraagent, vat_validation = await ContraagentService.create_contraagent(
        session=session,
        organization_id=current_org.id,
        created_by_id=current_user.id,
        contraagent_create=contraagent_in,
        validate_vat=validate_vat,
    )

    # Load related data
    await session.refresh(contraagent, ["accounting_account"])

    accounting_account_name = None
    if contraagent.accounting_account:
        accounting_account_name = contraagent.accounting_account.name

    response = ContraagentPublic(
        **contraagent.model_dump(),
        accounting_account_name=accounting_account_name,
    )

    # Add VAT validation info to response if available
    if vat_validation:
        response.vat_validation = vat_validation

    return response


@router.put("/{id}", response_model=ContraagentPublic)
async def update_contraagent(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    contraagent_in: ContraagentUpdate,
    validate_vat: bool = Query(True, description="Validate VAT number using VIES"),
) -> Any:
    """
    Update a contraagent. Requires at least manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    contraagent, vat_validation = await ContraagentService.update_contraagent(
        session=session,
        organization_id=current_org.id,
        contraagent_id=id,
        contraagent_update=contraagent_in,
        validate_vat=validate_vat,
    )

    # Load related data
    await session.refresh(contraagent, ["accounting_account"])

    accounting_account_name = None
    if contraagent.accounting_account:
        accounting_account_name = contraagent.accounting_account.name

    response = ContraagentPublic(
        **contraagent.model_dump(),
        accounting_account_name=accounting_account_name,
    )

    # Add VAT validation info to response if available
    if vat_validation:
        response.vat_validation = vat_validation

    return response


@router.delete("/{id}")
async def delete_contraagent(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Message:
    """
    Soft delete a contraagent. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    success = await ContraagentService.delete_contraagent(session, current_org.id, id)

    if not success:
        raise HTTPException(status_code=404, detail="Contraagent not found")

    return Message(message="Contraagent deleted successfully")


# VAT Validation endpoint
@router.post("/validate-vat")
async def validate_vat_number(
    vat_number: str = Query(..., description="VAT number to validate"),
) -> Any:
    """
    Validate VAT number using EU VIES system.
    """
    validation_result = await VIESValidator.validate_vat(vat_number)
    return validation_result


# Opening Balance endpoints
@router.post("/{id}/opening-balance")
async def set_opening_balance(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    debit_balance: Decimal = Query(Decimal("0"), description="Opening debit balance"),
    credit_balance: Decimal = Query(Decimal("0"), description="Opening credit balance"),
    description: Optional[str] = Query(
        None, description="Description for journal entry"
    ),
) -> Any:
    """
    Set opening balance for contraagent. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    (
        contraagent,
        journal_entry,
    ) = await OpeningBalancesService.set_contraagent_opening_balance(
        session=session,
        organization_id=current_org.id,
        contraagent_id=id,
        debit_balance=debit_balance,
        credit_balance=credit_balance,
        description=description,
        created_by_id=current_user.id,
    )

    return {
        "contraagent": contraagent,
        "journal_entry": journal_entry,
        "message": "Opening balance set successfully",
    }


@router.delete("/{id}/opening-balance")
async def remove_opening_balance(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Remove opening balance for contraagent. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    (
        contraagent,
        has_journal_entry,
    ) = await OpeningBalancesService.remove_contraagent_opening_balance(
        session=session,
        organization_id=current_org.id,
        contraagent_id=id,
        created_by_id=current_user.id,
    )

    return {
        "contraagent": contraagent,
        "journal_entry_created": has_journal_entry,
        "message": "Opening balance removed successfully",
    }


@router.get("/opening-balances/summary")
async def get_opening_balances_summary(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
) -> Any:
    """
    Get summary of all contraagent opening balances.
    """
    summary = await OpeningBalancesService.get_total_opening_balances(
        session=session, organization_id=current_org.id
    )

    return summary


# Bank Account endpoints
@router.get("/{id}/bank-accounts", response_model=ContraagentBankAccountsPublic)
async def read_contraagent_bank_accounts(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
) -> Any:
    """
    Get bank accounts for a contraagent.
    """
    # Verify contraagent exists and belongs to organization
    contraagent = await ContraagentService.get_contraagent_by_id(
        session, current_org.id, id
    )
    if not contraagent:
        raise HTTPException(status_code=404, detail="Contraagent not found")

    # Get bank accounts
    query = (
        select(ContraagentBankAccount)
        .where(ContraagentBankAccount.contraagent_id == id)
        .order_by(
            ContraagentBankAccount.is_primary.desc(),
            ContraagentBankAccount.date_created,
        )
    )

    result = await session.exec(query)
    bank_accounts = result.all()

    return ContraagentBankAccountsPublic(data=bank_accounts, count=len(bank_accounts))


@router.post("/{id}/bank-accounts", response_model=ContraagentBankAccountPublic)
async def create_contraagent_bank_account(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    id: uuid.UUID,
    bank_account_in: ContraagentBankAccountCreate,
) -> Any:
    """
    Add bank account to contraagent. Requires at least member role.
    """
    bank_account = await ContraagentService.add_bank_account(
        session=session,
        organization_id=current_org.id,
        contraagent_id=id,
        bank_account_create=bank_account_in,
    )

    return bank_account


@router.put(
    "/bank-accounts/{bank_account_id}", response_model=ContraagentBankAccountPublic
)
async def update_contraagent_bank_account(
    *,
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    bank_account_id: uuid.UUID,
    bank_account_in: ContraagentBankAccountUpdate,
) -> Any:
    """
    Update contraagent bank account. Requires at least member role.
    """
    bank_account = await ContraagentService.update_bank_account(
        session=session,
        organization_id=current_org.id,
        bank_account_id=bank_account_id,
        bank_account_update=bank_account_in,
    )

    return bank_account


@router.delete("/bank-accounts/{bank_account_id}")
async def delete_contraagent_bank_account(
    session: SessionDep,
    current_org: CurrentOrganization,
    membership: CurrentMembership,
    bank_account_id: uuid.UUID,
) -> Message:
    """
    Delete contraagent bank account. Requires manager role.
    """
    if not has_role_or_higher(membership.role, OrganizationRole.MANAGER):
        raise HTTPException(status_code=403, detail="Requires manager role")

    success = await ContraagentService.delete_bank_account(
        session, current_org.id, bank_account_id
    )

    if not success:
        raise HTTPException(status_code=404, detail="Bank account not found")

    return Message(message="Bank account deleted successfully")
