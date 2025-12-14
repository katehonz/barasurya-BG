from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.crud import currency as currency_crud, exchange_rate as exchange_rate_crud
from app.models import (
    CurrencyCreate,
    CurrencyUpdate,
    CurrencyPublic,
    CurrenciesPublic,
    ExchangeRatesPublic,
)
from app.services import ecb_service

router = APIRouter(prefix="/currencies", tags=["currencies"])


@router.get("", response_model=CurrenciesPublic)
def read_currencies(
    db: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve currencies.
    """
    count, currencies = currency_crud.get_multi(db, skip=skip, limit=limit)
    return {"data": currencies, "count": count}


@router.post("", response_model=CurrencyPublic)
def create_currency(
    db: SessionDep,
    current_user: CurrentUser,
    currency_in: CurrencyCreate,
) -> Any:
    """
    Create new currency.
    """
    new_currency = currency_crud.create(db, obj_in=currency_in)
    return new_currency


@router.put("/{id}", response_model=CurrencyPublic)
def update_currency(
    db: SessionDep,
    current_user: CurrentUser,
    id: UUID,
    currency_in: CurrencyUpdate,
) -> Any:
    """
    Update a currency.
    """
    db_currency = currency_crud.get(db, id=id)
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    updated_currency = currency_crud.update(db, db_obj=db_currency, obj_in=currency_in)
    return updated_currency


@router.get("/{id}", response_model=CurrencyPublic)
def read_currency(
    db: SessionDep,
    current_user: CurrentUser,
    id: UUID,
) -> Any:
    """
    Get currency by ID.
    """
    db_currency = currency_crud.get(db, id=id)
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    return db_currency


@router.delete("/{id}", response_model=CurrencyPublic)
def delete_currency(
    db: SessionDep,
    current_user: CurrentUser,
    id: UUID,
) -> Any:
    """
    Delete a currency.
    """
    db_currency = currency_crud.get(db, id=id)
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    deleted_currency = currency_crud.remove(db, id=id)
    return deleted_currency


@router.get("/exchange-rates", response_model=ExchangeRatesPublic, tags=["exchange-rates"])
def read_exchange_rates(
    db: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve exchange rates.
    """
    count, rates = exchange_rate_crud.get_multi(db, skip=skip, limit=limit)
    return {"data": rates, "count": count}


@router.post("/exchange-rates/update-ecb", response_model=dict, tags=["exchange-rates"])
async def update_ecb_rates(
    db: SessionDep,
    current_user: CurrentUser,
):
    """
    Update exchange rates from ECB.
    """
    count = await ecb_service.update_current_rates(db)
    return {"message": f"Successfully updated {count} exchange rates from ECB."}
