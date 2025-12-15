from fastapi import APIRouter

from app.api.routes import (
    accounts,
    ai_invoices,
    assets,
    bank_accounts,
    bank_transactions,
    contraagents,
    currencies,
    login,
    organizations,
    organization_settings,
    permissions,
    private,
    purchases,
    purchase_orders,
    quotations,
    recipes,
    sales,
    stores,
    stock_levels,
    users,
    utils,
    saft,
    payments,
    vat,
    journal_entries,
)
from app.core.config import settings
from app.sales.api import invoices_router

api_router = APIRouter()
api_router.include_router(accounts.router)
api_router.include_router(
    ai_invoices.router, prefix="/ai-invoices", tags=["ai-invoices"]
)
api_router.include_router(assets.router)
api_router.include_router(bank_accounts.router)
api_router.include_router(bank_transactions.router)
api_router.include_router(contraagents.router)
api_router.include_router(currencies.router)
api_router.include_router(organizations.router)
api_router.include_router(organization_settings.router)
api_router.include_router(login.router)
api_router.include_router(payments.router)
api_router.include_router(permissions.router)
api_router.include_router(purchases.router)
api_router.include_router(purchase_orders.router)
api_router.include_router(quotations.router)
api_router.include_router(recipes.router)
api_router.include_router(saft.router)
api_router.include_router(sales.router)
api_router.include_router(stores.router)
api_router.include_router(stock_levels.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(invoices_router, prefix="/invoices", tags=["invoices"])
api_router.include_router(vat.router, prefix="/vat", tags=["vat"])
api_router.include_router(journal_entries.router, prefix="/journal-entries", tags=["journal-entries"])


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
