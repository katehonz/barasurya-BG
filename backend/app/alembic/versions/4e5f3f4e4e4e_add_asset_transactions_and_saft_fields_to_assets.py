"""add asset_transactions and saft fields to assets

Revision ID: 4e5f3f4e4e4e
Revises: 3a3d9f3e3d3b
Create Date: 2025-12-14 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e5f3f4e4e4e'
down_revision = '3a3d9f3e3d3b'
branch_labels = None
depends_on = None


def upgrade():
    # This migration is now a no-op - all asset-related tables and columns
    # are created in d4e5f6a7b8c9_create_asset_tables.py
    pass


def downgrade():
    # No-op - see upgrade()
    pass
