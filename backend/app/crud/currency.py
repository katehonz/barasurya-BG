from typing import Optional
from uuid import UUID
from sqlmodel import Session, select, and_
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.currency import Currency, CurrencyCreate, CurrencyUpdate
from app.models.exchange_rate import ExchangeRate, ExchangeRateCreate


class CRUDCurrency(CRUDBase[Currency, CurrencyCreate, CurrencyUpdate]):
    def get_by_code(self, db: Session, code: str) -> Optional[Currency]:
        """Get currency by ISO code"""
        statement = select(Currency).where(Currency.code == code.upper())
        return db.exec(statement).first()

    def get_all(
        self, db: Session, skip: int = 0, limit: int = 100, active_only: bool = True
    ):
        """Get all currencies with pagination"""
        statement = select(Currency)

        if active_only:
            statement = statement.where(Currency.is_active == True)

        statement = statement.offset(skip).limit(limit).order_by(Currency.code)
        return db.exec(statement).all()

    def get_base_currency(self, db: Session) -> Optional[Currency]:
        """Get base currency"""
        statement = select(Currency).where(Currency.is_base_currency == True)
        return db.exec(statement).first()

    def create(self, db: Session, *, obj_in: CurrencyCreate) -> Currency:
        """Create new currency"""
        # Check if currency code already exists
        existing = self.get_by_code(db, obj_in.code)
        if existing:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail=f"Currency with code {obj_in.code} already exists",
            )

        # If this is set as base currency, unset any existing base currency
        if obj_in.is_base_currency:
            for curr in db.exec(
                select(Currency).where(Currency.is_base_currency == True)
            ).all():
                curr.is_base_currency = False

        currency = Currency.model_validate(obj_in)
        db.add(currency)
        db.commit()
        db.refresh(currency)
        return currency

    def update(
        self, db: Session, *, db_obj: Currency, obj_in: CurrencyUpdate
    ) -> Currency:
        """Update currency"""
        # If setting as base currency, unset others
        if obj_in.is_base_currency and not db_obj.is_base_currency:
            for curr in db.exec(
                select(Currency).where(Currency.is_base_currency == True)
            ).all():
                curr.is_base_currency = False

        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, currency_id: UUID) -> bool:
        """Delete currency (soft delete by setting is_active=False)"""
        currency = self.get(db, currency_id)
        if not currency:
            return False

        # Don't allow deletion of base currency
        if currency.is_base_currency:
            from fastapi import HTTPException

            raise HTTPException(status_code=400, detail="Cannot delete base currency")

        currency.is_active = False
        db.commit()
        return True

    def restore(self, db: Session, currency_id: UUID) -> Optional[Currency]:
        """Restore soft-deleted currency"""
        currency = self.get(db, currency_id)
        if not currency:
            return None

        currency.is_active = True
        db.commit()
        db.refresh(currency)
        return currency


class CRUDExchangeRate(CRUDBase[ExchangeRate, ExchangeRateCreate, dict]):
    def get_rate(
        self, db: Session, from_currency_id: UUID, to_currency_id: UUID, valid_date
    ) -> Optional[ExchangeRate]:
        """Get exchange rate for specific currencies and date"""
        statement = (
            select(ExchangeRate)
            .options(selectinload(ExchangeRate.from_currency))
            .options(selectinload(ExchangeRate.to_currency))
            .where(
                and_(
                    ExchangeRate.from_currency_id == from_currency_id,
                    ExchangeRate.to_currency_id == to_currency_id,
                    ExchangeRate.valid_date == valid_date,
                    ExchangeRate.is_active == True,
                )
            )
        )
        return db.exec(statement).first()

    def get_latest_rate(
        self, db: Session, from_currency_id: UUID, to_currency_id: UUID
    ) -> Optional[ExchangeRate]:
        """Get latest exchange rate for currency pair"""
        statement = (
            select(ExchangeRate)
            .options(selectinload(ExchangeRate.from_currency))
            .options(selectinload(ExchangeRate.to_currency))
            .where(
                and_(
                    ExchangeRate.from_currency_id == from_currency_id,
                    ExchangeRate.to_currency_id == to_currency_id,
                    ExchangeRate.is_active == True,
                )
            )
            .order_by(ExchangeRate.valid_date.desc())
        )
        return db.exec(statement).first()

    def create(self, db: Session, *, obj_in: ExchangeRateCreate) -> ExchangeRate:
        """Create new exchange rate"""
        # Check if rate already exists for this date and currency pair
        existing = self.get_rate(
            db,
            obj_in.from_currency_id,
            obj_in.to_currency_id,
            obj_in.valid_date,
        )
        if existing:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400,
                detail=f"Exchange rate for {obj_in.valid_date} already exists",
            )

        # Calculate reverse rate
        obj_data = obj_in.model_dump()
        if obj_in.rate and obj_in.rate > 0:
            obj_data["reverse_rate"] = 1 / obj_in.rate

        exchange_rate = ExchangeRate(**obj_data)
        db.add(exchange_rate)
        db.commit()
        db.refresh(exchange_rate)
        return exchange_rate

    def convert_amount(
        self,
        db: Session,
        amount: float,
        from_currency_id: UUID,
        to_currency_id: UUID,
        valid_date=None,
    ) -> tuple[float, Optional[ExchangeRate]]:
        """Convert amount from one currency to another"""
        if from_currency_id == to_currency_id:
            return amount, None

        # Get appropriate exchange rate
        if valid_date:
            rate = self.get_rate(db, from_currency_id, to_currency_id, valid_date)
        else:
            rate = self.get_latest_rate(db, from_currency_id, to_currency_id)

        if not rate:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=400, detail="No exchange rate found for currency pair"
            )

        converted_amount = float(rate.rate) * amount
        return converted_amount, rate


currency = CRUDCurrency(Currency)
exchange_rate = CRUDExchangeRate(ExchangeRate)
