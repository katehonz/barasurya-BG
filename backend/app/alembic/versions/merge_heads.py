"""merge heads

Revision ID: merge_heads
Revises: c3d4e5f6a7b8, f6a7b8c9d0e1
Create Date: 2025-12-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = ['c3d4e5f6a7b8', 'f6a7b8c9d0e1']
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
