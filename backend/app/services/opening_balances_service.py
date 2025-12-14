from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.contraagent import Contraagent
from app.models.journal_entry import JournalEntry, JournalEntryCreate
from app.models.entry_line import EntryLine, EntryLineCreate
from app.models.account import Account


class OpeningBalancesService:
    """Service for managing contraagent opening balances"""

    @staticmethod
    async def set_contraagent_opening_balance(
        session: AsyncSession,
        organization_id: UUID,
        contraagent_id: UUID,
        debit_balance: Decimal = Decimal("0"),
        credit_balance: Decimal = Decimal("0"),
        description: Optional[str] = None,
        created_by_id: Optional[UUID] = None,
    ) -> tuple[Contraagent, Optional[JournalEntry]]:
        """Set opening balance for contraagent and create journal entry"""

        # Get contraagent
        query = select(Contraagent).where(
            Contraagent.id == contraagent_id,
            Contraagent.organization_id == organization_id,
        )
        result = await session.exec(query)
        contraagent = result.first()

        if not contraagent:
            raise ValueError("Contraagent not found")

        # Update contraagent opening balances
        contraagent.opening_debit_balance = debit_balance
        contraagent.opening_credit_balance = credit_balance
        contraagent.date_updated = datetime.utcnow()

        # Create journal entry if there's a balance
        journal_entry = None
        if debit_balance > 0 or credit_balance > 0:
            journal_entry = (
                await OpeningBalancesService._create_opening_balance_journal_entry(
                    session=session,
                    organization_id=organization_id,
                    contraagent=contraagent,
                    debit_balance=debit_balance,
                    credit_balance=credit_balance,
                    description=description
                    or f"Opening balance for {contraagent.name}",
                    created_by_id=created_by_id,
                )
            )

        await session.commit()
        await session.refresh(contraagent)

        return contraagent, journal_entry

    @staticmethod
    async def _create_opening_balance_journal_entry(
        session: AsyncSession,
        organization_id: UUID,
        contraagent: Contraagent,
        debit_balance: Decimal,
        credit_balance: Decimal,
        description: str,
        created_by_id: Optional[UUID],
    ) -> JournalEntry:
        """Create journal entry for contraagent opening balance"""

        # Get or create appropriate accounts based on contraagent type
        if contraagent.is_customer:
            # Customer - use Accounts Receivable
            receivable_account = await OpeningBalancesService._get_account_by_code(
                session,
                organization_id,
                "1210",  # Typical AR account code
            )
            if not receivable_account:
                raise ValueError("Accounts Receivable account not found")

            contraact_account = receivable_account
        elif contraagent.is_supplier:
            # Supplier - use Accounts Payable
            payable_account = await OpeningBalancesService._get_account_by_code(
                session,
                organization_id,
                "4010",  # Typical AP account code
            )
            if not payable_account:
                raise ValueError("Accounts Payable account not found")

            contraact_account = payable_account
        else:
            raise ValueError("Contraagent must be either customer or supplier")

        # Get opening balance equity account
        opening_balance_account = await OpeningBalancesService._get_account_by_code(
            session,
            organization_id,
            "3010",  # Typical opening balance equity account
        )
        if not opening_balance_account:
            raise ValueError("Opening Balance equity account not found")

        # Create journal entry
        journal_entry = JournalEntry(
            date=datetime.utcnow().date(),
            description=description,
            reference=f"OB-{contraagent.id.hex[:8].upper()}",
            organization_id=organization_id,
            created_by_id=created_by_id,
            is_opening_balance=True,
        )

        session.add(journal_entry)
        await session.flush()  # Get the ID

        # Create entry lines
        if debit_balance > 0:
            # Contraagent debit (asset increase or liability decrease)
            debit_line = EntryLine(
                journal_entry_id=journal_entry.id,
                account_id=contraact_account.id,
                debit_amount=debit_balance,
                credit_amount=Decimal("0"),
                description=f"{contraagent.name} - Opening Debit Balance",
            )
            session.add(debit_line)

            # Opening balance equity credit
            credit_line = EntryLine(
                journal_entry_id=journal_entry.id,
                account_id=opening_balance_account.id,
                debit_amount=Decimal("0"),
                credit_amount=debit_balance,
                description="Opening Balance Equity",
            )
            session.add(credit_line)

        if credit_balance > 0:
            # Opening balance equity debit
            debit_line = EntryLine(
                journal_entry_id=journal_entry.id,
                account_id=opening_balance_account.id,
                debit_amount=credit_balance,
                credit_amount=Decimal("0"),
                description="Opening Balance Equity",
            )
            session.add(debit_line)

            # Contraagent credit (liability increase or asset decrease)
            credit_line = EntryLine(
                journal_entry_id=journal_entry.id,
                account_id=contraact_account.id,
                debit_amount=Decimal("0"),
                credit_amount=credit_balance,
                description=f"{contraagent.name} - Opening Credit Balance",
            )
            session.add(credit_line)

        await session.refresh(journal_entry)
        return journal_entry

    @staticmethod
    async def _get_account_by_code(
        session: AsyncSession, organization_id: UUID, account_code: str
    ) -> Optional[Account]:
        """Get account by code within organization"""
        query = select(Account).where(
            Account.code == account_code, Account.organization_id == organization_id
        )
        result = await session.exec(query)
        return result.first()

    @staticmethod
    async def get_contraagents_with_opening_balances(
        session: AsyncSession, organization_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Contraagent], int]:
        """Get contraagents that have opening balances"""

        query = (
            select(Contraagent)
            .where(
                Contraagent.organization_id == organization_id,
                (Contraagent.opening_debit_balance > 0)
                | (Contraagent.opening_credit_balance > 0),
            )
            .order_by(Contraagent.name)
        )

        # Get total count
        count_query = select(Contraagent).where(
            Contraagent.organization_id == organization_id,
            (Contraagent.opening_debit_balance > 0)
            | (Contraagent.opening_credit_balance > 0),
        )
        count_result = await session.exec(count_query)
        total = len(count_result.all())

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await session.exec(query)
        contraagents = result.all()

        return contraagents, total

    @staticmethod
    async def remove_contraagent_opening_balance(
        session: AsyncSession,
        organization_id: UUID,
        contraagent_id: UUID,
        created_by_id: Optional[UUID] = None,
    ) -> tuple[Contraagent, bool]:
        """Remove contraagent opening balance and create reversing journal entry"""

        # Get contraagent
        query = select(Contraagent).where(
            Contraagent.id == contraagent_id,
            Contraagent.organization_id == organization_id,
        )
        result = await session.exec(query)
        contraagent = result.first()

        if not contraagent:
            raise ValueError("Contraagent not found")

        # Store current balances
        old_debit_balance = contraagent.opening_debit_balance
        old_credit_balance = contraagent.opening_credit_balance

        # Clear opening balances
        contraagent.opening_debit_balance = Decimal("0")
        contraagent.opening_credit_balance = Decimal("0")
        contraagent.date_updated = datetime.utcnow()

        # Create reversing journal entry if there were balances
        journal_entry = None
        if old_debit_balance > 0 or old_credit_balance > 0:
            journal_entry = (
                await OpeningBalancesService._create_opening_balance_journal_entry(
                    session=session,
                    organization_id=organization_id,
                    contraagent=contraagent,
                    debit_balance=old_credit_balance,  # Reverse the balances
                    credit_balance=old_debit_balance,
                    description=f"Remove opening balance for {contraagent.name}",
                    created_by_id=created_by_id,
                )
            )

        await session.commit()
        await session.refresh(contraagent)

        return contraagent, journal_entry is not None

    @staticmethod
    async def get_total_opening_balances(
        session: AsyncSession, organization_id: UUID
    ) -> dict:
        """Get total opening balances for all contraagents"""

        query = select(Contraagent).where(
            Contraagent.organization_id == organization_id
        )
        result = await session.exec(query)
        contraagents = result.all()

        total_debit = Decimal("0")
        total_credit = Decimal("0")
        customer_debit = Decimal("0")
        customer_credit = Decimal("0")
        supplier_debit = Decimal("0")
        supplier_credit = Decimal("0")

        for contraagent in contraagents:
            if contraagent.opening_debit_balance > 0:
                total_debit += contraagent.opening_debit_balance
                if contraagent.is_customer:
                    customer_debit += contraagent.opening_debit_balance
                elif contraagent.is_supplier:
                    supplier_debit += contraagent.opening_debit_balance

            if contraagent.opening_credit_balance > 0:
                total_credit += contraagent.opening_credit_balance
                if contraagent.is_customer:
                    customer_credit += contraagent.opening_credit_balance
                elif contraagent.is_supplier:
                    supplier_credit += contraagent.opening_credit_balance

        return {
            "total_debit_balance": total_debit,
            "total_credit_balance": total_credit,
            "customer_debit_balance": customer_debit,
            "customer_credit_balance": customer_credit,
            "supplier_debit_balance": supplier_debit,
            "supplier_credit_balance": supplier_credit,
            "contraagent_count": len(contraagents),
            "contraagents_with_balances": len(
                [
                    c
                    for c in contraagents
                    if c.opening_debit_balance > 0 or c.opening_credit_balance > 0
                ]
            ),
        }
