import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.account_transaction import AccountTransaction
    from app.models.bank_account import BankAccount
    from app.models.bank_import import BankImport
    from app.models.bank_profile import BankProfile
    from app.models.bank_statement import BankStatement
    from app.models.bank_transaction import BankTransaction
    from app.models.contraagent import Contraagent
    from app.models.currency import Currency
    from app.models.customer import Customer
    from app.models.customer_type import CustomerType
    from app.models.invoice import Invoice
    from app.models.item import Item
    from app.models.item_category import ItemCategory
    from app.models.item_unit import ItemUnit
    from app.models.journal_entry import JournalEntry
    from app.models.organization_member import OrganizationMember
    from app.models.payable import Payable
    from app.models.payment import Payment
    from app.models.permission import Permission
    from app.models.purchase import Purchase
    from app.models.purchase_return import PurchaseReturn
    from app.models.receivable import Receivable
    from app.models.role import Role
    from app.models.sale import Sale
    from app.models.sale_return import SaleReturn
    from app.models.stock_adjustment import StockAdjustment
    from app.models.stock_transfer import StockTransfer
    from app.models.store import Store
    from app.models.supplier import Supplier
    from app.models.vat_return import VatReturn
    from app.models.vat_sales_register import VatSalesRegister
    from app.models.vat_purchase_register import VatPurchaseRegister


class OrganizationBase(BaseModel):
    name: str = Field(min_length=1, max_length=255, index=True)
    slug: str = Field(min_length=1, max_length=100, unique=True, index=True)
    is_active: bool = True
    region_code: str | None = Field(default=None)
    default_currency_code: str | None = Field(
        default="BGN", max_length=3, description="Default currency code (ISO 4217)"
    )
    base_currency_id: uuid.UUID | None = Field(
        default=None, foreign_key="currencies.id", description="Base currency reference"
    )
    tax_basis: str | None = Field(default=None)
    in_eurozone: bool = Field(
        default=False, description="Whether organization is in Eurozone"
    )
    eurozone_entry_date: datetime | None = Field(
        default=None, description="Date when organization entered Eurozone"
    )
    accounts_receivable_account_id: uuid.UUID | None = Field(
        default=None, foreign_key="account.id"
    )
    sales_revenue_account_id: uuid.UUID | None = Field(
        default=None, foreign_key="account.id"
    )
    vat_payable_account_id: uuid.UUID | None = Field(
        default=None, foreign_key="account.id"
    )
    inventory_account_id: uuid.UUID | None = Field(
        default=None, foreign_key="account.id"
    )
    accounts_payable_account_id: uuid.UUID | None = Field(
        default=None, foreign_key="account.id"
    )
    vat_deductible_account_id: uuid.UUID | None = Field(
        default=None, foreign_key="account.id"
    )
    cash_account_id: uuid.UUID | None = Field(default=None, foreign_key="account.id")


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None
    region_code: str | None = Field(default=None)
    default_currency_code: str | None = Field(default=None, max_length=3)
    base_currency_id: uuid.UUID | None = Field(default=None)
    tax_basis: str | None = Field(default=None)
    in_eurozone: bool | None = None
    eurozone_entry_date: datetime | None = Field(default=None)
    accounts_receivable_account_id: uuid.UUID | None = Field(default=None)
    sales_revenue_account_id: uuid.UUID | None = Field(default=None)
    vat_payable_account_id: uuid.UUID | None = Field(default=None)
    inventory_account_id: uuid.UUID | None = Field(default=None)
    accounts_payable_account_id: uuid.UUID | None = Field(default=None)
    vat_deductible_account_id: uuid.UUID | None = Field(default=None)
    cash_account_id: uuid.UUID | None = Field(default=None)


class Organization(OrganizationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)
    eik: str | None = Field(default=None)

    # Relationships
    members: list["OrganizationMember"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    items: list["Item"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    item_categories: list["ItemCategory"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    item_units: list["ItemUnit"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    stores: list["Store"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    suppliers: list["Supplier"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    customer_types: list["CustomerType"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    customers: list["Customer"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    purchases: list["Purchase"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    sales: list["Sale"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    accounts: list["Account"] = Relationship(
        back_populates="organization",
        cascade_delete=True,
        sa_relationship_kwargs={"foreign_keys": "[Account.organization_id]"},
    )
    account_transactions: list["AccountTransaction"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    payments: list["Payment"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    stock_adjustments: list["StockAdjustment"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    stock_transfers: list["StockTransfer"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    payables: list["Payable"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    receivables: list["Receivable"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    sale_returns: list["SaleReturn"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    purchase_returns: list["PurchaseReturn"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    roles: list["Role"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    permissions: list["Permission"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    invoices: list["Invoice"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    bank_accounts: list["BankAccount"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    bank_transactions: list["BankTransaction"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    bank_statements: list["BankStatement"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    bank_imports: list["BankImport"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    bank_profiles: list["BankProfile"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    journal_entries: list["JournalEntry"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    vat_returns: list["VatReturn"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    vat_sales_registers: list["VatSalesRegister"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    vat_purchase_registers: list["VatPurchaseRegister"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    contraagents: list["Contraagent"] = Relationship(
        back_populates="organization", cascade_delete=True
    )
    base_currency: Optional["Currency"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Organization.base_currency_id]"}
    )


class OrganizationPublic(OrganizationBase):
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class OrganizationsPublic(BaseModel):
    data: list[OrganizationPublic]
    count: int
