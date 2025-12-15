import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, UniqueConstraint

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.account_transaction import AccountTransaction
    from app.models.asset import Asset
    from app.models.asset_transaction import AssetTransaction
    from app.models.bank_account import BankAccount
    from app.models.bank_import import BankImport
    from app.models.bank_profile import BankProfile
    from app.models.bank_statement import BankStatement
    from app.models.bank_transaction import BankTransaction
    from app.models.contraagent import Contraagent
    from app.models.invoice import Invoice
    from app.models.item import Item
    from app.models.journal_entry import JournalEntry
    from app.models.measurement_unit import MeasurementUnit
    from app.models.organization_member import OrganizationMember
    from app.models.organization_settings import OrganizationSettings
    from app.models.payable import Payable
    from app.models.payment import Payment
    from app.models.permission import Permission
    from app.models.product import Product
    from app.models.purchase import Purchase
    from app.models.purchase_order import PurchaseOrder
    from app.models.purchase_return import PurchaseReturn
    from app.models.quotation import Quotation
    from app.models.receivable import Receivable
    from app.models.role import Role
    from app.models.sale import Sale
    from app.models.sale_return import SaleReturn
    from app.models.stock_adjustment import StockAdjustment
    from app.models.stock_transfer import StockTransfer
    from app.models.store import Store
    from app.models.vat_return import VatReturn
    from app.models.vat_sales_register import VatSalesRegister
    from app.models.warehouse import Warehouse


class OrganizationBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    name_latin: str | None = Field(default=None, max_length=255)
    name_cyrillic: str | None = Field(default=None, max_length=255)

    # Registration Info
    registration_number: str | None = Field(default=None, max_length=50)  # ЕИК/БУЛСТАТ
    vat_number: str | None = Field(default=None, max_length=50)  # VAT number

    # Address Info
    street_name: str | None = Field(default=None, max_length=255)
    building_number: str | None = Field(default=None, max_length=50)
    building: str | None = Field(default=None, max_length=50)
    postal_code: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, max_length=100)
    region: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default="BG", max_length=100)

    # Contact Info
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    website: str | None = Field(default=None, max_length=255)

    is_active: bool = Field(default=True)
    is_vat_registered: bool = Field(default=False)

    # Additional SAF-T Fields
    tax_authority: str | None = Field(default=None, max_length=255)
    tax_accounting_basis: str | None = Field(default=None, max_length=50) # Cash or Accrual
    currency_code: str | None = Field(default="BGN", max_length=3)
    date_format: str | None = Field(default="YYYY-MM-DD", max_length=20)
    fiscal_year_start_date: str | None = Field(default="01-01", max_length=5) # MM-DD

    # Bank Information (Primary Bank Account)
    bank_name: str | None = Field(default=None, max_length=255)
    bank_account_number: str | None = Field(default=None, max_length=50)
    bank_iban: str | None = Field(default=None, max_length=50)
    bank_swift: str | None = Field(default=None, max_length=20)

    # Legal representative (SAF-T)
    legal_representative_name: str | None = Field(default=None, max_length=255)
    legal_representative_id: str | None = Field(default=None, max_length=50) # EGN/LNCH

    # Notes
    notes: str | None = Field(default=None, max_length=1000)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationBase):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)


class Organization(OrganizationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships - Core
    members: List["OrganizationMember"] = Relationship(back_populates="organization")
    accounts: List["Account"] = Relationship(back_populates="organization")
    account_transactions: List["AccountTransaction"] = Relationship(back_populates="organization")
    contraagents: List["Contraagent"] = Relationship(back_populates="organization")
    items: List["Item"] = Relationship(back_populates="organization")
    products: List["Product"] = Relationship(back_populates="organization")

    # Relationships - Banking
    bank_accounts: List["BankAccount"] = Relationship(back_populates="organization")
    bank_imports: List["BankImport"] = Relationship(back_populates="organization")
    bank_profiles: List["BankProfile"] = Relationship(back_populates="organization")
    bank_statements: List["BankStatement"] = Relationship(back_populates="organization")
    bank_transactions: List["BankTransaction"] = Relationship(back_populates="organization")

    # Relationships - Sales
    invoices: List["Invoice"] = Relationship(back_populates="organization")
    quotations: List["Quotation"] = Relationship(back_populates="organization")
    sales: List["Sale"] = Relationship(back_populates="organization")
    sale_returns: List["SaleReturn"] = Relationship(back_populates="organization")
    receivables: List["Receivable"] = Relationship(back_populates="organization")

    # Relationships - Purchases
    purchases: List["Purchase"] = Relationship(back_populates="organization")
    purchase_orders: List["PurchaseOrder"] = Relationship(back_populates="organization")
    purchase_returns: List["PurchaseReturn"] = Relationship(back_populates="organization")
    payables: List["Payable"] = Relationship(back_populates="organization")

    # Relationships - Assets
    assets: List["Asset"] = Relationship(back_populates="organization")
    asset_transactions: List["AssetTransaction"] = Relationship(back_populates="organization")

    # Relationships - Inventory
    stores: List["Store"] = Relationship(back_populates="organization")
    warehouses: List["Warehouse"] = Relationship(back_populates="organization")
    stock_adjustments: List["StockAdjustment"] = Relationship(back_populates="organization")
    stock_transfers: List["StockTransfer"] = Relationship(back_populates="organization")

    # Relationships - Accounting
    journal_entries: List["JournalEntry"] = Relationship(back_populates="organization")
    payments: List["Payment"] = Relationship(back_populates="organization")

    # Relationships - VAT
    vat_returns: List["VatReturn"] = Relationship(back_populates="organization")
    vat_sales_registers: List["VatSalesRegister"] = Relationship(back_populates="organization")

    # Relationships - Settings
    measurement_units: List["MeasurementUnit"] = Relationship(back_populates="organization")
    permissions: List["Permission"] = Relationship(back_populates="organization")
    roles: List["Role"] = Relationship(back_populates="organization")
    settings: "OrganizationSettings" = Relationship(back_populates="organization")

    __table_args__ = (UniqueConstraint("name"),)


class OrganizationPublic(OrganizationBase):
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class OrganizationsPublic(BaseModel):
    data: list[OrganizationPublic]
    count: int
