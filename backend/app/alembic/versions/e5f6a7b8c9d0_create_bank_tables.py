"""Create bank tables

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2024-12-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e5f6a7b8c9d0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create bank_account table
    op.create_table(
        'bank_account',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_no', sa.String(length=50), nullable=False),
        sa.Column('iban', sa.String(length=34), nullable=False),
        sa.Column('bic', sa.String(length=11), nullable=True),
        sa.Column('account_type', sa.String(length=20), nullable=False, server_default='current'),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='BGN'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('bank_name', sa.String(length=255), nullable=False),
        sa.Column('bank_code', sa.String(length=20), nullable=True),
        sa.Column('branch_name', sa.String(length=255), nullable=True),
        sa.Column('initial_balance', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0.00'),
        sa.Column('current_balance', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0.00'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_account_iban'), 'bank_account', ['iban'], unique=False)
    op.create_index(op.f('ix_bank_account_organization_id'), 'bank_account', ['organization_id'], unique=False)

    # Create bank_profile table
    op.create_table(
        'bank_profile',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('buffer_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('iban', sa.String(length=34), nullable=True),
        sa.Column('bic', sa.String(length=11), nullable=True),
        sa.Column('bank_name', sa.String(length=255), nullable=True),
        sa.Column('currency_code', sa.String(length=3), nullable=False, server_default='BGN'),
        sa.Column('import_format', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('saltedge_connection_id', sa.String(length=100), nullable=True),
        sa.Column('saltedge_account_id', sa.String(length=100), nullable=True),
        sa.Column('auto_sync_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_synced_at', sa.DateTime(), nullable=True),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bank_account_id'], ['account.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['buffer_account_id'], ['account.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_profile_iban'), 'bank_profile', ['iban'], unique=False)
    op.create_index(op.f('ix_bank_profile_organization_id'), 'bank_profile', ['organization_id'], unique=False)

    # Create bank_import table
    op.create_table(
        'bank_import',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_profile_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('import_type', sa.String(length=20), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('import_format', sa.String(length=50), nullable=True),
        sa.Column('imported_at', sa.DateTime(), nullable=False),
        sa.Column('transactions_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_credit', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0.00'),
        sa.Column('total_debit', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0.00'),
        sa.Column('created_journal_entries', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='in_progress'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('period_from', sa.Date(), nullable=True),
        sa.Column('period_to', sa.Date(), nullable=True),
        sa.Column('saltedge_attempt_id', sa.String(length=100), nullable=True),
        sa.Column('journal_entry_ids', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bank_profile_id'], ['bank_profile.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_import_organization_id'), 'bank_import', ['organization_id'], unique=False)
    op.create_index(op.f('ix_bank_import_bank_profile_id'), 'bank_import', ['bank_profile_id'], unique=False)

    # Create bank_statement table
    op.create_table(
        'bank_statement',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('statement_no', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('statement_date', sa.Date(), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=False),
        sa.Column('opening_balance', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0.00'),
        sa.Column('closing_balance', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0.00'),
        sa.Column('total_debits', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0.00'),
        sa.Column('total_credits', sa.Numeric(precision=18, scale=2), nullable=False, server_default='0.00'),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('file_format', sa.String(length=50), nullable=True),
        sa.Column('import_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bank_account_id'], ['bank_account.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_statement_organization_id'), 'bank_statement', ['organization_id'], unique=False)
    op.create_index(op.f('ix_bank_statement_bank_account_id'), 'bank_statement', ['bank_account_id'], unique=False)

    # Create bank_transaction table
    op.create_table(
        'bank_transaction',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_import_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('bank_profile_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('journal_entry_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('booking_date', sa.Date(), nullable=False),
        sa.Column('value_date', sa.Date(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='BGN'),
        sa.Column('is_credit', sa.Boolean(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reference', sa.String(length=255), nullable=True),
        sa.Column('transaction_id', sa.String(length=255), nullable=True),
        sa.Column('counterpart_name', sa.String(length=255), nullable=True),
        sa.Column('counterpart_iban', sa.String(length=34), nullable=True),
        sa.Column('counterpart_bic', sa.String(length=11), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bank_account_id'], ['bank_account.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['bank_import_id'], ['bank_import.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['bank_profile_id'], ['bank_profile.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['journal_entry_id'], ['journal_entry.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_transaction_organization_id'), 'bank_transaction', ['organization_id'], unique=False)
    op.create_index(op.f('ix_bank_transaction_bank_account_id'), 'bank_transaction', ['bank_account_id'], unique=False)
    op.create_index(op.f('ix_bank_transaction_bank_import_id'), 'bank_transaction', ['bank_import_id'], unique=False)
    op.create_index(op.f('ix_bank_transaction_bank_profile_id'), 'bank_transaction', ['bank_profile_id'], unique=False)
    op.create_index(op.f('ix_bank_transaction_journal_entry_id'), 'bank_transaction', ['journal_entry_id'], unique=False)


def downgrade() -> None:
    op.drop_table('bank_transaction')
    op.drop_table('bank_statement')
    op.drop_table('bank_import')
    op.drop_table('bank_profile')
    op.drop_table('bank_account')
