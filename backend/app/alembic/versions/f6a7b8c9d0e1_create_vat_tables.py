"""Create VAT tables

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2024-12-14 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f6a7b8c9d0e1'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create vat_return table
    op.create_table(
        'vat_return',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('period_year', sa.Integer(), nullable=False),
        sa.Column('period_month', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('total_sales_taxable', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('total_sales_vat', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('total_purchases_taxable', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('total_purchases_vat', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('total_deductible_vat', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('vat_payable', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('vat_refundable', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('submission_date', sa.Date(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'period_year', 'period_month', name='uq_vat_return_period')
    )
    op.create_index(op.f('ix_vat_return_organization_id'), 'vat_return', ['organization_id'], unique=False)

    # Create vat_sales_register table
    op.create_table(
        'vat_sales_register',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('period_year', sa.Integer(), nullable=False),
        sa.Column('period_month', sa.Integer(), nullable=False),
        sa.Column('document_date', sa.Date(), nullable=False),
        sa.Column('tax_event_date', sa.Date(), nullable=False),
        sa.Column('document_type', sa.String(length=20), nullable=False),
        sa.Column('document_number', sa.String(length=50), nullable=False),
        sa.Column('sales_operation', sa.String(length=50), nullable=True),
        sa.Column('recipient_name', sa.String(length=255), nullable=False),
        sa.Column('recipient_vat_number', sa.String(length=20), nullable=True),
        sa.Column('recipient_country', sa.String(length=2), nullable=False, server_default='BG'),
        sa.Column('recipient_eik', sa.String(length=20), nullable=True),
        sa.Column('recipient_city', sa.String(length=100), nullable=True),
        sa.Column('taxable_base', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('vat_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('vat_amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('vat_operation_code', sa.String(length=20), nullable=True),
        sa.Column('column_code', sa.String(length=20), nullable=True),
        sa.Column('vies_indicator', sa.String(length=5), nullable=True),
        sa.Column('reverse_charge_subcode', sa.String(length=5), nullable=True),
        sa.Column('is_triangular_operation', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_art_21_service', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vat_sales_register_organization_id'), 'vat_sales_register', ['organization_id'], unique=False)
    op.create_index(op.f('ix_vat_sales_register_invoice_id'), 'vat_sales_register', ['invoice_id'], unique=False)

    # Create vat_purchase_register table
    op.create_table(
        'vat_purchase_register',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('document_type_table', sa.String(length=50), nullable=True),
        sa.Column('period_year', sa.Integer(), nullable=False),
        sa.Column('period_month', sa.Integer(), nullable=False),
        sa.Column('document_date', sa.Date(), nullable=False),
        sa.Column('tax_event_date', sa.Date(), nullable=False),
        sa.Column('document_type', sa.String(length=20), nullable=False),
        sa.Column('document_number', sa.String(length=50), nullable=False),
        sa.Column('purchase_operation', sa.String(length=50), nullable=True),
        sa.Column('supplier_name', sa.String(length=255), nullable=False),
        sa.Column('supplier_vat_number', sa.String(length=20), nullable=True),
        sa.Column('supplier_country', sa.String(length=2), nullable=False, server_default='BG'),
        sa.Column('supplier_eik', sa.String(length=20), nullable=True),
        sa.Column('supplier_city', sa.String(length=100), nullable=True),
        sa.Column('taxable_base', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('vat_rate', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('vat_amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('is_deductible', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('deductible_vat_amount', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('vat_operation_code', sa.String(length=20), nullable=True),
        sa.Column('column_code', sa.String(length=20), nullable=True),
        sa.Column('deductible_credit_type', sa.String(length=20), nullable=False, server_default='full'),
        sa.Column('vies_indicator', sa.String(length=5), nullable=True),
        sa.Column('reverse_charge_subcode', sa.String(length=5), nullable=True),
        sa.Column('is_triangular_operation', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_art_21_service', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vat_purchase_register_organization_id'), 'vat_purchase_register', ['organization_id'], unique=False)


def downgrade() -> None:
    op.drop_table('vat_purchase_register')
    op.drop_table('vat_sales_register')
    op.drop_table('vat_return')
