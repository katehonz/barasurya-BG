from fastapi import APIRouter

from app.api.routes import (
    accounts,
    assets,
    bank_accounts,
    bank_transactions,
    customer_types,
    customers,
    item_categories,
    item_units,
    items,
    login,
    organizations,
    permissions,
    private,
    purchases,
    sales,
    stores,
    stock_levels,
    suppliers,
    users,
    utils,
    saft,
    payments,
)
from app.core.config import settings
from app.sales.api import invoices_router

api_router = APIRouter()
api_router.include_router(accounts.router)
api_router.include_router(assets.router)
api_router.include_router(bank_accounts.router)
api_router.include_router(bank_transactions.router)
api_router.include_router(customer_types.router)
api_router.include_router(customers.router)
api_router.include_router(organizations.router)
api_router.include_router(item_categories.router)
api_router.include_router(item_units.router)
api_router.include_router(items.router)
api_router.include_router(login.router)
api_router.include_router(payments.router)
api_router.include_router(permissions.router)
api_router.include_router(purchases.router)
api_router.include_router(sales.router)
api_router.include_router(saft.router)
api_router.include_router(stores.router)
api_router.include_router(stock_levels.router)
api_router.include_router(suppliers.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(invoices_router, prefix="/invoices", tags=["invoices"])


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
