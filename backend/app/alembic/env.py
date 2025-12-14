import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None

from app.models import BaseModel  # noqa
from app.core.config import settings # noqa

# Explicitly import all models to ensure they are registered with BaseModel.metadata
from app.models.main import *
from app.models.purchase_item import *
from app.models.purchase_return_item import *
from app.models.role_permission import *
from app.models.sale_item import *
from app.models.sale_return_item import *
from app.models.user_role import *
from app.models.organization_member import *
from app.models.account_transaction import *
from app.models.purchase_return import *
from app.models.sale_return import *
from app.models.stock_adjustment import *
from app.models.stock_transfer import *
from app.models.role import *
from app.models.permission import *
from app.models.user import *
from app.models.saft.asset_movement_type import *
from app.models.saft.country import *
from app.models.saft.iban_format import *
from app.models.saft.inventory_type import *
from app.models.saft.invoice_type import *
from app.models.saft.nc8_taric import *
from app.models.saft.payment_method import *
from app.models.saft.stock_movement_type import *
from app.models.saft.vat_tax_type import *
from app.models.asset_transaction import *
from app.models.bank_account import *
from app.models.bank_transaction import *
from app.models.bank_statement import *
from app.models.bank_import import *
from app.models.bank_profile import *
from app.models.vat_return import *
from app.models.vat_purchase_register import *
from app.models.vat_sales_register import *
from app.models.invoice_line import *
from app.models.payment import *
from app.models.asset import *
from app.models.asset_depreciation_schedule import *
from app.models.entry_line import *
from app.models.journal_entry import *
from app.models.payable import *
from app.models.purchase import *
from app.models.receivable import *
from app.models.sale import *
from app.models.contraagent_bank_account import *
from app.models.contraagent import *
from app.models.account import *
from app.models.currency import *
from app.models.exchange_rate import *
from app.models.invoice import *
from app.models.product import *
from app.models.measurement_unit import *
from app.models.product_unit import *
from app.models.lot import *
from app.models.stock_level import *
from app.models.stock_movement import *
from app.models.organization import *
from app.models.store import *
from app.models.recipe import *
from app.models.recipe_item import *
from app.models.purchase_order_line import *
from app.models.quotation_line import *
from app.models.warehouse import *
from app.models.purchase_order import *
from app.models.quotation import *
from app.models.item import *


target_metadata = BaseModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    return str(settings.SQLALCHEMY_DATABASE_URI)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
