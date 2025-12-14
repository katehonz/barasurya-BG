import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, UniqueConstraint

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.contraagent import Contraagent
    from app.models.document_type import DocumentType
    from app.models.item import Item
    from app.models.user import User
    from app.models.invoice import Invoice
    from app.models.payable import Payable
    from app.models.receivable import Receivable
    from app.models.purchase import Purchase
    from app.models.sale import Sale
    from app.models.purchase_order import PurchaseOrder
    from app.models.quotation import Quotation
    from app.models.product_category import ProductCategory
    from app.models.asset import Asset
    from app.models.asset_category import AssetCategory
    from app.models.asset_transaction import AssetTransaction


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
    
    # Relationships
    users: List["User"] = Relationship(back_populates="organization")
    contraagents: List["Contraagent"] = Relationship(back_populates="organization")
    accounts: List["Account"] = Relationship(back_populates="organization")
    document_types: List["DocumentType"] = Relationship(back_populates="organization")
    items: List["Item"] = Relationship(back_populates="organization")
    invoices: List["Invoice"] = Relationship(back_populates="organization")
    payables: List["Payable"] = Relationship(back_populates="organization")
    receivables: List["Receivable"] = Relationship(back_populates="organization")
    purchases: List["Purchase"] = Relationship(back_populates="organization")
    sales: List["Sale"] = Relationship(back_populates="organization")
    purchase_orders: List["PurchaseOrder"] = Relationship(back_populates="organization")
    quotations: List["Quotation"] = Relationship(back_populates="organization")
    product_categories: List["ProductCategory"] = Relationship(back_populates="organization")
    assets: List["Asset"] = Relationship(back_populates="organization")
    asset_categories: List["AssetCategory"] = Relationship(back_populates="organization")
    asset_transactions: List["AssetTransaction"] = Relationship(back_populates="organization")

    __table_args__ = (UniqueConstraint("name"),)


class OrganizationPublic(OrganizationBase):
    id: uuid.UUID
    date_created: datetime
    date_updated: datetime


class OrganizationsPublic(BaseModel):
    data: list[OrganizationPublic]
    count: int