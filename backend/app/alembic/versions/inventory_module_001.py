"""Add inventory module tables (products, warehouses, stock)

Revision ID: inventory_module_001
Revises: 581f3a2b4c5d
Create Date: 2024-12-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'inventory_module_001'
down_revision = '581f3a2b4c5d'
branch_labels = None
depends_on = None


def upgrade():
    # Products table
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('sku', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(20), nullable=False, server_default='goods'),
        sa.Column('price', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('cost', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('unit', sa.String(20), nullable=False, server_default='бр.'),
        sa.Column('barcode', sa.String(50), nullable=True),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=False, server_default='20'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('track_inventory', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('opening_quantity', sa.Numeric(15, 4), nullable=False, server_default='0'),
        sa.Column('opening_cost', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('expense_account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('revenue_account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('cn_code', sa.String(10), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_organization_id', 'products', ['organization_id'])
    op.create_index('ix_products_sku', 'products', ['sku'])
    op.create_index('ix_products_barcode', 'products', ['barcode'])

    # Measurement units table
    op.create_table(
        'measurement_units',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('name_bg', sa.String(100), nullable=False),
        sa.Column('name_en', sa.String(100), nullable=True),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('is_base', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_measurement_units_organization_id', 'measurement_units', ['organization_id'])
    op.create_index('ix_measurement_units_code', 'measurement_units', ['code'])

    # Product units table (multi-unit support)
    op.create_table(
        'product_units',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('measurement_unit_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversion_factor', sa.Numeric(15, 6), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('barcode', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['measurement_unit_id'], ['measurement_units.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_product_units_product_id', 'product_units', ['product_id'])
    op.create_index('ix_product_units_measurement_unit_id', 'product_units', ['measurement_unit_id'])

    # Warehouses table
    op.create_table(
        'warehouses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('country', sa.String(3), nullable=False, server_default='BG'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('costing_method', sa.String(20), nullable=False, server_default='weighted_average'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_warehouses_organization_id', 'warehouses', ['organization_id'])
    op.create_index('ix_warehouses_code', 'warehouses', ['code'])

    # Lots table (batch/serial tracking)
    op.create_table(
        'lots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lot_number', sa.String(50), nullable=False),
        sa.Column('manufacture_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('supplier_lot_number', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_lots_organization_id', 'lots', ['organization_id'])
    op.create_index('ix_lots_product_id', 'lots', ['product_id'])
    op.create_index('ix_lots_lot_number', 'lots', ['lot_number'])

    # Stock levels table (current inventory by product/warehouse)
    op.create_table(
        'stock_levels',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity_on_hand', sa.Numeric(15, 4), nullable=False, server_default='0'),
        sa.Column('quantity_reserved', sa.Numeric(15, 4), nullable=False, server_default='0'),
        sa.Column('quantity_available', sa.Numeric(15, 4), nullable=False, server_default='0'),
        sa.Column('minimum_quantity', sa.Numeric(15, 4), nullable=False, server_default='0'),
        sa.Column('reorder_point', sa.Numeric(15, 4), nullable=False, server_default='0'),
        sa.Column('average_cost', sa.Numeric(15, 4), nullable=True),
        sa.Column('last_cost', sa.Numeric(15, 4), nullable=True),
        sa.Column('total_value', sa.Numeric(15, 2), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'product_id', 'warehouse_id', name='uq_stock_level_product_warehouse')
    )
    op.create_index('ix_stock_levels_organization_id', 'stock_levels', ['organization_id'])
    op.create_index('ix_stock_levels_product_id', 'stock_levels', ['product_id'])
    op.create_index('ix_stock_levels_warehouse_id', 'stock_levels', ['warehouse_id'])

    # Stock movements table (inventory transactions)
    op.create_table(
        'stock_movements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('document_no', sa.String(50), nullable=True),
        sa.Column('movement_type', sa.String(30), nullable=False),
        sa.Column('movement_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quantity', sa.Numeric(15, 4), nullable=False),
        sa.Column('unit_cost', sa.Numeric(15, 4), nullable=True),
        sa.Column('unit_price', sa.Numeric(15, 4), nullable=True),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('computed_unit_cost', sa.Numeric(15, 4), nullable=True),
        sa.Column('computed_total_cost', sa.Numeric(15, 2), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_warehouse_id'], ['warehouses.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['lot_id'], ['lots.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stock_movements_organization_id', 'stock_movements', ['organization_id'])
    op.create_index('ix_stock_movements_product_id', 'stock_movements', ['product_id'])
    op.create_index('ix_stock_movements_warehouse_id', 'stock_movements', ['warehouse_id'])
    op.create_index('ix_stock_movements_movement_date', 'stock_movements', ['movement_date'])
    op.create_index('ix_stock_movements_movement_type', 'stock_movements', ['movement_type'])


def downgrade():
    op.drop_table('stock_movements')
    op.drop_table('stock_levels')
    op.drop_table('lots')
    op.drop_table('warehouses')
    op.drop_table('product_units')
    op.drop_table('measurement_units')
    op.drop_table('products')
