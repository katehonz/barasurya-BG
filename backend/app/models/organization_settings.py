"""
Organization Settings model.

Stores per-organization configuration for:
- SMTP server settings
- Azure Document Intelligence settings
- Default accounting accounts
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship

from app.models import BaseModel
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.account import Account


class OrganizationSettingsBase(BaseModel):
    """Base model for organization settings."""
    # SMTP Settings (stored as JSON)
    smtp_host: str | None = Field(default=None, max_length=255, description="SMTP сървър")
    smtp_port: int | None = Field(default=587, description="SMTP порт")
    smtp_username: str | None = Field(default=None, max_length=255, description="SMTP потребител")
    smtp_password: str | None = Field(default=None, max_length=255, description="SMTP парола")
    smtp_use_tls: bool = Field(default=True, description="Използвай TLS")
    smtp_from_email: str | None = Field(default=None, max_length=255, description="Имейл подател")
    smtp_from_name: str | None = Field(default=None, max_length=255, description="Име на подател")

    # Azure Document Intelligence Settings
    azure_endpoint: str | None = Field(default=None, max_length=500, description="Azure endpoint URL")
    azure_api_key: str | None = Field(default=None, max_length=255, description="Azure API ключ")
    azure_model_id: str | None = Field(default="prebuilt-invoice", max_length=100, description="Azure model ID")


class OrganizationSettingsCreate(BaseModel):
    """Schema for creating organization settings."""
    # SMTP Settings
    smtp_host: str | None = None
    smtp_port: int | None = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    smtp_from_email: str | None = None
    smtp_from_name: str | None = None

    # Azure Settings
    azure_endpoint: str | None = None
    azure_api_key: str | None = None
    azure_model_id: str | None = "prebuilt-invoice"

    # Default Accounts (UUIDs)
    default_clients_account_id: uuid.UUID | None = None
    default_suppliers_account_id: uuid.UUID | None = None
    default_vat_purchases_account_id: uuid.UUID | None = None
    default_vat_sales_account_id: uuid.UUID | None = None
    default_revenue_account_id: uuid.UUID | None = None
    default_cash_account_id: uuid.UUID | None = None
    default_bank_account_id: uuid.UUID | None = None


class OrganizationSettingsUpdate(BaseModel):
    """Schema for updating organization settings."""
    # SMTP Settings
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str | None = None

    # Azure Settings
    azure_endpoint: str | None = None
    azure_api_key: str | None = None
    azure_model_id: str | None = None

    # Default Accounts
    default_clients_account_id: uuid.UUID | None = None
    default_suppliers_account_id: uuid.UUID | None = None
    default_vat_purchases_account_id: uuid.UUID | None = None
    default_vat_sales_account_id: uuid.UUID | None = None
    default_revenue_account_id: uuid.UUID | None = None
    default_cash_account_id: uuid.UUID | None = None
    default_bank_account_id: uuid.UUID | None = None


class SmtpSettingsUpdate(BaseModel):
    """Schema for updating only SMTP settings."""
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool | None = None
    smtp_from_email: str | None = None
    smtp_from_name: str | None = None


class AzureSettingsUpdate(BaseModel):
    """Schema for updating only Azure settings."""
    azure_endpoint: str | None = None
    azure_api_key: str | None = None
    azure_model_id: str | None = None


class DefaultAccountsUpdate(BaseModel):
    """Schema for updating only default accounts."""
    default_clients_account_id: uuid.UUID | None = None
    default_suppliers_account_id: uuid.UUID | None = None
    default_vat_purchases_account_id: uuid.UUID | None = None
    default_vat_sales_account_id: uuid.UUID | None = None
    default_revenue_account_id: uuid.UUID | None = None
    default_cash_account_id: uuid.UUID | None = None
    default_bank_account_id: uuid.UUID | None = None


class OrganizationSettings(OrganizationSettingsBase, table=True):
    """Organization settings table model."""
    __tablename__ = "organization_settings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", unique=True, index=True)

    # Default Accounts (Foreign Keys to Account table)
    default_clients_account_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="account.id",
        description="Сметка Клиенти (вземания)"
    )
    default_suppliers_account_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="account.id",
        description="Сметка Доставчици (задължения)"
    )
    default_vat_purchases_account_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="account.id",
        description="Сметка ДДС Покупки"
    )
    default_vat_sales_account_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="account.id",
        description="Сметка ДДС Продажби"
    )
    default_revenue_account_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="account.id",
        description="Сметка Приходи"
    )
    default_cash_account_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="account.id",
        description="Сметка Каса"
    )
    default_bank_account_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="account.id",
        description="Сметка Банка"
    )

    date_created: datetime = Field(default_factory=utcnow)
    date_updated: datetime = Field(default_factory=utcnow)

    # Relationships
    organization: "Organization" = Relationship(back_populates="settings")

    # Account relationships
    default_clients_account: "Account" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[OrganizationSettings.default_clients_account_id]"}
    )
    default_suppliers_account: "Account" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[OrganizationSettings.default_suppliers_account_id]"}
    )
    default_vat_purchases_account: "Account" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[OrganizationSettings.default_vat_purchases_account_id]"}
    )
    default_vat_sales_account: "Account" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[OrganizationSettings.default_vat_sales_account_id]"}
    )
    default_revenue_account: "Account" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[OrganizationSettings.default_revenue_account_id]"}
    )
    default_cash_account: "Account" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[OrganizationSettings.default_cash_account_id]"}
    )
    default_bank_account: "Account" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[OrganizationSettings.default_bank_account_id]"}
    )


class OrganizationSettingsPublic(OrganizationSettingsBase):
    """Public schema for organization settings."""
    id: uuid.UUID
    organization_id: uuid.UUID

    # Default Account IDs
    default_clients_account_id: uuid.UUID | None = None
    default_suppliers_account_id: uuid.UUID | None = None
    default_vat_purchases_account_id: uuid.UUID | None = None
    default_vat_sales_account_id: uuid.UUID | None = None
    default_revenue_account_id: uuid.UUID | None = None
    default_cash_account_id: uuid.UUID | None = None
    default_bank_account_id: uuid.UUID | None = None

    date_created: datetime
    date_updated: datetime


class SmtpTestResult(BaseModel):
    """Result of SMTP connection test."""
    success: bool
    message: str
