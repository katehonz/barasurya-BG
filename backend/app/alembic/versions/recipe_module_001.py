"""Add recipe and recipe_item tables for manufacturing module

Revision ID: recipe_module_001
Revises: inventory_module_001
Create Date: 2024-12-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'recipe_module_001'
down_revision = 'inventory_module_001'
branch_labels = None
depends_on = None


def upgrade():
    # Recipe table - производствена рецепта (Bill of Materials)
    op.create_table(
        'recipe',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('output_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('output_quantity', sa.Numeric(15, 4), nullable=False, server_default='1'),
        sa.Column('unit', sa.String(20), nullable=False, server_default='бр.'),
        sa.Column('version', sa.String(20), nullable=False, server_default='1.0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('production_cost', sa.Numeric(15, 4), nullable=False, server_default='0'),
        sa.Column('notes', sa.String(1000), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('date_updated', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.id']),
        sa.ForeignKeyConstraint(['output_item_id'], ['item.id']),
    )
    op.create_index('ix_recipe_organization_id', 'recipe', ['organization_id'])
    op.create_index('ix_recipe_code', 'recipe', ['organization_id', 'code'], unique=True)
    op.create_index('ix_recipe_output_item_id', 'recipe', ['output_item_id'])

    # RecipeItem table - компонент/суровина в рецепта
    op.create_table(
        'recipeitem',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('line_no', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('quantity', sa.Numeric(15, 4), nullable=False),
        sa.Column('unit', sa.String(20), nullable=False, server_default='бр.'),
        sa.Column('wastage_percent', sa.Numeric(5, 2), nullable=False, server_default='0'),
        sa.Column('cost', sa.Numeric(15, 4), nullable=False, server_default='0'),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['item_id'], ['item.id']),
    )
    op.create_index('ix_recipeitem_recipe_id', 'recipeitem', ['recipe_id'])
    op.create_index('ix_recipeitem_item_id', 'recipeitem', ['item_id'])


def downgrade():
    op.drop_index('ix_recipeitem_item_id', table_name='recipeitem')
    op.drop_index('ix_recipeitem_recipe_id', table_name='recipeitem')
    op.drop_table('recipeitem')

    op.drop_index('ix_recipe_output_item_id', table_name='recipe')
    op.drop_index('ix_recipe_code', table_name='recipe')
    op.drop_index('ix_recipe_organization_id', table_name='recipe')
    op.drop_table('recipe')
