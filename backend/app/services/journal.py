
from sqlmodel import Session
from app.models.journal_entry import JournalEntry, JournalEntryCreate
from app.models.entry_line import EntryLine, EntryLineCreate
from app.models.organization import Organization
from app.models.user import User
import uuid
from datetime import date


class JournalService:
    def __init__(self, session: Session, current_user: User, current_organization: Organization):
        self.session = session
        self.current_user = current_user
        self.current_organization = current_organization

    def create_journal_entry_for_payment(self, payment: Any) -> JournalEntry:
        journal_entry = JournalEntry.model_validate(
            JournalEntryCreate(
                date=payment.date_payment,
                description=f"Payment {payment.id}",
                document_date=payment.date_payment,
                document_reference=f"Payment:{payment.id}",
            ),
            update={
                "organization_id": self.current_organization.id,
                "created_by_id": self.current_user.id,
            },
        )

        # TODO: Get accounts from organization settings
        cash_account_id = self.current_organization.cash_account_id or uuid.uuid4()
        accounts_payable_account_id = self.current_organization.accounts_payable_account_id or uuid.uuid4()

        debit_account_id = accounts_payable_account_id
        credit_account_id = cash_account_id
        debit_description = "Accounts Payable"
        credit_description = "Cash"

        # if payment is for something else, change the debit account
        if payment.subject_type == "expense":
            # TODO: Get expense account id
            debit_account_id = uuid.uuid4()
            debit_description = "Expense"

        lines = [
            EntryLineCreate(
                account_id=debit_account_id,
                debit=payment.amount,
                credit=0,
                description=debit_description,
            ),
            EntryLineCreate(
                account_id=credit_account_id,
                debit=0,
                credit=payment.amount,
                description=credit_description,
            ),
        ]

        journal_entry.lines = [
            EntryLine.model_validate(
                line,
                update={
                    "organization_id": self.current_organization.id,
                    "created_by_id": self.current_user.id,
                },
            )
            for line in lines
        ]

        self.session.add(journal_entry)
        self.session.commit()
        self.session.refresh(journal_entry)
        return journal_entry
