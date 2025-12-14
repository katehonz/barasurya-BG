"""Add multi-tenant architecture

Revision ID: add_multi_tenant
Revises: 77539d0fc467
Create Date: 2025-12-14

This migration:
1. Creates organization table
2. Creates organization_member table (junction table with roles)
3. Adds current_organization_id to user table
4. Replaces owner_id with organization_id and created_by_id for all business models

IMPORTANT: This is a destructive migration. Run it on a fresh database or backup data first.
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'add_multi_tenant'
down_revision = '77539d0fc467'
branch_labels = None
depends_on = None


# Tables that need owner_id -> organization_id + created_by_id conversion
TABLES_TO_CONVERT = [
    'account',
    'account_transaction',
    'customer',
    'customer_type',
    'item',
    'item_category',
    'item_unit',
    'payment',
    'purchase',
    'sale',
    'stock_adjustment',
    'store',
    'supplier',
    'role',
    'permission',
]

# Tables from later migrations that also need conversion
TABLES_WITH_OWNER_ID = [
    'payable',
    'receivable',
    'purchase_return',
    'sale_return',
    'stock_transfer',
]


def upgrade():
    # 1. Create organization table
    op.create_table('organization',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('slug', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('date_created', sa.DateTime(), nullable=False),
        sa.Column('date_updated', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_organization'))
    )
    op.create_index(op.f('ix_organization_name'), 'organization', ['name'], unique=False)
    op.create_index(op.f('ix_organization_slug'), 'organization', ['slug'], unique=True)

    # 2. Create organization_member table
    op.create_table('organizationmember',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('role', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False, server_default='member'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('date_joined', sa.DateTime(), nullable=False),
        sa.Column('date_updated', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], name=op.f('fk_organizationmember_organization_id_organization'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_organizationmember_user_id_user'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_organizationmember'))
    )
    op.create_index(op.f('ix_organizationmember_organization_id'), 'organizationmember', ['organization_id'], unique=False)
    op.create_index(op.f('ix_organizationmember_user_id'), 'organizationmember', ['user_id'], unique=False)
    # Unique constraint: user can only have one membership per organization
    op.create_unique_constraint('uq_organizationmember_user_org', 'organizationmember', ['user_id', 'organization_id'])

    # 3. Add current_organization_id to user table
    op.add_column('user', sa.Column('current_organization_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        op.f('fk_user_current_organization_id_organization'),
        'user', 'organization',
        ['current_organization_id'], ['id'],
        ondelete='SET NULL'
    )

    # 4. Convert tables: add organization_id, created_by_id, drop owner_id
    all_tables = TABLES_TO_CONVERT + TABLES_WITH_OWNER_ID

    for table_name in all_tables:
        # Check if table exists before modifying
        try:
            # Add organization_id column
            op.add_column(table_name, sa.Column('organization_id', sa.Uuid(), nullable=True))
            op.create_index(f'ix_{table_name}_organization_id', table_name, ['organization_id'], unique=False)
            op.create_foreign_key(
                f'fk_{table_name}_organization_id_organization',
                table_name, 'organization',
                ['organization_id'], ['id'],
                ondelete='CASCADE'
            )

            # Add created_by_id column (if not already exists like in permission/role)
            if table_name not in ['permission', 'role']:
                op.add_column(table_name, sa.Column('created_by_id', sa.Uuid(), nullable=True))
                op.create_foreign_key(
                    f'fk_{table_name}_created_by_id_user',
                    table_name, 'user',
                    ['created_by_id'], ['id'],
                    ondelete='CASCADE'
                )

            # Drop owner_id column and its foreign key
            if table_name in ['permission', 'role']:
                # These have owner_id from the previous migration
                op.drop_constraint(f'fk_{table_name}_owner_id_user', table_name, type_='foreignkey')
                op.drop_column(table_name, 'owner_id')
            else:
                # Standard tables
                try:
                    op.drop_constraint(f'fk_{table_name}_owner_id_user', table_name, type_='foreignkey')
                except:
                    pass  # Constraint might not exist
                try:
                    op.drop_column(table_name, 'owner_id')
                except:
                    pass  # Column might not exist
        except Exception as e:
            print(f"Warning: Could not convert table {table_name}: {e}")
            continue


def downgrade():
    # Reverse the migration - this will lose data

    all_tables = TABLES_TO_CONVERT + TABLES_WITH_OWNER_ID

    for table_name in all_tables:
        try:
            # Drop created_by_id column
            if table_name not in ['permission', 'role']:
                try:
                    op.drop_constraint(f'fk_{table_name}_created_by_id_user', table_name, type_='foreignkey')
                except:
                    pass
                try:
                    op.drop_column(table_name, 'created_by_id')
                except:
                    pass

            # Drop organization_id column
            try:
                op.drop_constraint(f'fk_{table_name}_organization_id_organization', table_name, type_='foreignkey')
            except:
                pass
            try:
                op.drop_index(f'ix_{table_name}_organization_id', table_name=table_name)
            except:
                pass
            try:
                op.drop_column(table_name, 'organization_id')
            except:
                pass

            # Re-add owner_id column
            op.add_column(table_name, sa.Column('owner_id', sa.Uuid(), nullable=True))
            op.create_foreign_key(
                f'fk_{table_name}_owner_id_user',
                table_name, 'user',
                ['owner_id'], ['id'],
                ondelete='CASCADE'
            )
        except Exception as e:
            print(f"Warning: Could not revert table {table_name}: {e}")
            continue

    # Drop current_organization_id from user
    op.drop_constraint(op.f('fk_user_current_organization_id_organization'), 'user', type_='foreignkey')
    op.drop_column('user', 'current_organization_id')

    # Drop organization_member table
    op.drop_index(op.f('ix_organizationmember_user_id'), table_name='organizationmember')
    op.drop_index(op.f('ix_organizationmember_organization_id'), table_name='organizationmember')
    op.drop_constraint('uq_organizationmember_user_org', 'organizationmember', type_='unique')
    op.drop_table('organizationmember')

    # Drop organization table
    op.drop_index(op.f('ix_organization_slug'), table_name='organization')
    op.drop_index(op.f('ix_organization_name'), table_name='organization')
    op.drop_table('organization')
