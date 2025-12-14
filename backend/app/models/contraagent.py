import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.contraagent_bank_account import ContraagentBankAccount
    from app.models.organization import Organization
    from app.models.user import User


class ContraagentBase(BaseModel):
    # Basic Information
    name: str = Field(min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    website: str | None = Field(default=None, max_length=255)
    fax: str | None = Field(default=None, max_length=50)
    
    # Classification
    is_company: bool = Field(default=True)
    is_customer: bool = Field(default=False)
    is_supplier: bool = Field(default=False)
    is_active: bool = Field(default=True)
    
    # Registration Numbers
    registration_number: str | None = Field(default=None, max_length=50)  # ЕИК/БУЛСТАТ
    vat_number: str | None = Field(default=None, max_length=50)  # VAT number
    
    # SAF-T Address Information
    street_name: str | None = Field(default=None, max_length=255)
    building_number: str | None = Field(default=None, max_length=50)
    building: str | None = Field(default=None, max_length=50)
    postal_code: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, max_length=100)
    region: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default="BG", max_length=100)
    additional_address_detail: str | None = Field(default=None, max_length=255)
    
    # Contact Person Information (SAF-T)
    contact_person_title: str | None = Field(default=None, max_length=50)
    contact_person_first_name: str | None = Field(default=None, max_length=100)
    contact_person_last_name: str | None = Field(default=None, max_length=100)
    
    # Tax Information
    tax_type: str | None = Field(default=None, max_length=50)  # VAT, EXEMPT, etc.
    tax_authority: str | None = Field(default=None, max_length=255)
    tax_verification_date: datetime | None = Field(default=None)
    
    # SAF-T Classification
    self_billing_indicator: bool = Field(default=False)
    related_party: bool = Field(default=False)
    related_party_start_date: datetime | None = Field(default=None)
    related_party_end_date: datetime | None = Field(default=None)
    
    # Bank Information
    iban_number: str | None = Field(default=None, max_length=50)
    bank_account_number: str | None = Field(default=None, max_length=50)
    bank_sort_code: str | None = Field(default=None, max_length=50)
    
    # Accounting Information
    accounting_account_id: uuid.UUID | None = Field(default=None, foreign_key="account.id")
    
    # Opening Balances
    opening_debit_balance: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    opening_credit_balance: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    closing_debit_balance: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    closing_credit_balance: Decimal = Field(default=0, max_digits=15, decimal_places=2)
    
    # Price List (for future use)
    # price_list_id: uuid.UUID | None = Field(default=None, foreign_key="price_list.id")
    
    # Names (Cyrillic/Latin support)
    name_latin: str | None = Field(default=None, max_length=255)
    name_cyrillic: str | None = Field(default=None, max_length=255)
    
    # Notes
    notes: str | None = Field(default=None, max_length=1000)


class ContraagentCreate(ContraagentBase):
    pass


class ContraagentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    website: str | None = Field(default=None, max_length=255)
    fax: str | None = Field(default=None, max_length=50)
    
    is_company: bool | None = None
    is_customer: bool | None = None
    is_supplier: bool | None = None
    is_active: bool | None = None
    
    registration_number: str | None = Field(default=None, max_length=50)
    vat_number: str | None = Field(default=None, max_length=50)
    
    street_name: str | None = Field(default=None, max_length=255)
    building_number: str | None = Field(default=None, max_length=50)
    building: str | None = Field(default=None, max_length=50)
    postal_code: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, max_length=100)
    region: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    additional_address_detail: str | None = Field(default=None, max_length=255)
    
    contact_person_title: str | None = Field(default=None, max_length=50)
    contact_person_first_name: str | None = Field(default=None, max_length=100)
    contact_person_last_name: str | None = Field(default=None, max_length=100)
    
    tax_type: str | None = Field(default=None, max_length=50)
    tax_authority: str | None = Field(default=None, max_length=255)
    tax_verification_date: datetime | None = None
    
    self_billing_indicator: bool | None = None
    related_party: bool | None = None
    related_party_start_date: datetime | None = None
    related_party_end_date: datetime | None = None
    
    iban_number: str | None = Field(default=None, max_length=50)
    bank_account_number: str | None = Field(default=None, max_length=50)
    bank_sort_code: str | None = Field(default=None, max_length=50)
    
    accounting_account_id: uuid.UUID | None = None
    price_list_id: uuid.UUID | None = None
    
    opening_debit_balance: Decimal | None = None
    opening_credit_balance: Decimal | None = None
    
    name_latin: str | None = Field(default=None, max_length=255)
    name_cyrillic: str | None = Field(default=None, max_length=255)
    
    notes: str | None = Field(default=None, max_length=1000)


class Contraagent(ContraagentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    organization_id: uuid.UUID = Field(
        foreign_key="organization.id", nullable=False, ondelete="CASCADE", index=True
    )
    created_by_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="contraagents")
    created_by: "User" = Relationship()
    accounting_account: "Account" = Relationship(back_populates="contraagents")
    
    # Bank Accounts
    bank_accounts: list["ContraagentBankAccount"] = Relationship(
        back_populates="contraagent", cascade_delete=True
    )


class ContraagentPublic(ContraagentBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by_id: uuid.UUID
    date_created: datetime
    date_updated: datetime
    accounting_account_name: str | None = None


class ContraagentsPublic(BaseModel):
    data: list[ContraagentPublic]
    count: int