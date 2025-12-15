"""Create document uploads and extracted invoices tables

Revision ID: add_ai_invoice_tables
Revises: initial
Create Date: 2025-01-15 10:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "add_ai_invoice_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create document_uploads table
    op.create_table(
        "document_uploads",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("local_path", sa.String(length=1024), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("file_type", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("document_type", sa.String(length=50), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("azure_document_id", sa.String(length=255), nullable=True),
        sa.Column(
            "azure_result", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column("date_created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_updated", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_document_uploads_organization_id"),
        "document_uploads",
        ["organization_id"],
        unique=False,
    )

    # Create extracted_invoices table
    op.create_table(
        "extracted_invoices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column("document_upload_id", sa.UUID(), nullable=False),
        sa.Column("approved_by_id", sa.UUID(), nullable=True),
        sa.Column("invoice_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("confidence_score", sa.Decimal(precision=5, scale=4), nullable=True),
        sa.Column("invoice_number", sa.String(length=255), nullable=True),
        sa.Column("invoice_date", sa.Date(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("vendor_name", sa.String(length=255), nullable=True),
        sa.Column("vendor_address", sa.String(), nullable=True),
        sa.Column("vendor_vat_number", sa.String(length=50), nullable=True),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("customer_address", sa.String(), nullable=True),
        sa.Column("customer_vat_number", sa.String(length=50), nullable=True),
        sa.Column("subtotal", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("tax_amount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("total_amount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("line_items", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.String(), nullable=True),
        sa.Column("converted_invoice_id", sa.UUID(), nullable=True),
        sa.Column("converted_invoice_type", sa.String(), nullable=True),
        sa.Column("oss_country", sa.String(length=2), nullable=True),
        sa.Column("oss_vat_rate", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("date_created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_updated", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["approved_by_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["document_upload_id"],
            ["document_uploads.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_upload_id"),
    )
    op.create_index(
        op.f("ix_extracted_invoices_organization_id"),
        "extracted_invoices",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_extracted_invoices_organization_id"), table_name="extracted_invoices"
    )
    op.drop_table("extracted_invoices")
    op.drop_index(
        op.f("ix_document_uploads_organization_id"), table_name="document_uploads"
    )
    op.drop_table("document_uploads")
