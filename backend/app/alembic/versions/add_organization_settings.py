"""Create organization_settings table

Revision ID: add_organization_settings
Revises: add_ai_invoice_tables
Create Date: 2025-01-15 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "add_organization_settings"
down_revision: Union[str, None] = "add_ai_invoice_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organization_settings table
    op.create_table(
        "organization_settings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),

        # SMTP Settings
        sa.Column("smtp_host", sa.String(length=255), nullable=True),
        sa.Column("smtp_port", sa.Integer(), nullable=True, default=587),
        sa.Column("smtp_username", sa.String(length=255), nullable=True),
        sa.Column("smtp_password", sa.String(length=255), nullable=True),
        sa.Column("smtp_use_tls", sa.Boolean(), nullable=False, default=True),
        sa.Column("smtp_from_email", sa.String(length=255), nullable=True),
        sa.Column("smtp_from_name", sa.String(length=255), nullable=True),

        # Azure Document Intelligence Settings
        sa.Column("azure_endpoint", sa.String(length=500), nullable=True),
        sa.Column("azure_api_key", sa.String(length=255), nullable=True),
        sa.Column("azure_model_id", sa.String(length=100), nullable=True, default="prebuilt-invoice"),

        # Default Accounting Accounts
        sa.Column("default_clients_account_id", sa.UUID(), nullable=True),
        sa.Column("default_suppliers_account_id", sa.UUID(), nullable=True),
        sa.Column("default_vat_purchases_account_id", sa.UUID(), nullable=True),
        sa.Column("default_vat_sales_account_id", sa.UUID(), nullable=True),
        sa.Column("default_revenue_account_id", sa.UUID(), nullable=True),
        sa.Column("default_cash_account_id", sa.UUID(), nullable=True),
        sa.Column("default_bank_account_id", sa.UUID(), nullable=True),

        # Timestamps
        sa.Column("date_created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_updated", sa.DateTime(timezone=True), nullable=False),

        # Constraints
        sa.ForeignKeyConstraint(["organization_id"], ["organization.id"]),
        sa.ForeignKeyConstraint(["default_clients_account_id"], ["account.id"]),
        sa.ForeignKeyConstraint(["default_suppliers_account_id"], ["account.id"]),
        sa.ForeignKeyConstraint(["default_vat_purchases_account_id"], ["account.id"]),
        sa.ForeignKeyConstraint(["default_vat_sales_account_id"], ["account.id"]),
        sa.ForeignKeyConstraint(["default_revenue_account_id"], ["account.id"]),
        sa.ForeignKeyConstraint(["default_cash_account_id"], ["account.id"]),
        sa.ForeignKeyConstraint(["default_bank_account_id"], ["account.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id"),
    )
    op.create_index(
        op.f("ix_organization_settings_organization_id"),
        "organization_settings",
        ["organization_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_organization_settings_organization_id"), table_name="organization_settings"
    )
    op.drop_table("organization_settings")
