from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, Session, SQLModel
from sqlalchemy import Index, UniqueConstraint, CheckConstraint

from app.models.base import BaseModel


class ExchangeRateBase(BaseModel):
    from_currency_id: UUID = Field(
        ..., foreign_key="currencies.id", description="Source currency ID"
    )
    to_currency_id: UUID = Field(
        ..., foreign_key="currencies.id", description="Target currency ID"
    )
    rate: Decimal = Field(
        ...,
        decimal_places=6,
        max_digits=15,
        description="Exchange rate (from_currency -> to_currency)",
    )
    reverse_rate: Optional[Decimal] = Field(
        default=None,
        decimal_places=6,
        max_digits=15,
        description="Reverse exchange rate",
    )
    valid_date: date = Field(..., description="Date when this rate is valid")
    rate_source: str = Field(
        default="manual",
        max_length=20,
        description="Source of the rate: manual, bnb, ecb, api",
    )
    bnb_rate_id: Optional[str] = Field(
        default=None, max_length=50, description="BNB rate identifier"
    )
    ecb_rate_id: Optional[str] = Field(
        default=None, max_length=50, description="ECB rate identifier"
    )
    is_active: bool = Field(default=True, description="Whether this rate is active")
    notes: Optional[str] = Field(
        default=None, max_length=500, description="Additional notes about the rate"
    )


class ExchangeRate(ExchangeRateBase, table=True):
    __tablename__ = "exchange_rates"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)

    # Database constraints and indexes
    __table_args__ = (
        UniqueConstraint(
            "from_currency_id",
            "to_currency_id",
            "valid_date",
            name="uq_exchange_rate_pair_date",
        ),
        Index("ix_exchange_rate_valid_date", "valid_date"),
        Index("ix_exchange_rate_rate_source", "rate_source"),
        Index("ix_exchange_rate_is_active", "is_active"),
        Index("ix_exchange_rate_bnb_rate_id", "bnb_rate_id"),
        CheckConstraint("rate > 0", name="ck_exchange_rate_positive"),
        CheckConstraint(
            "rate_source IN ('manual', 'bnb', 'ecb', 'api')",
            name="ck_exchange_rate_source",
        ),
    )

    # Relationships
    from_currency: "Currency" = Relationship(
        back_populates="exchange_rates_from",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRate.from_currency_id]"},
    )
    to_currency: "Currency" = Relationship(
        back_populates="exchange_rates_to",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRate.to_currency_id]"},
    )

    def calculate_reverse_rate(self) -> Decimal:
        """Calculate reverse rate from forward rate"""
        if self.rate and self.rate > 0:
            return Decimal("1") / self.rate
        return Decimal("0")

    def is_valid_for_date(self, check_date: date) -> bool:
        """Check if this rate is valid for the given date"""
        return self.valid_date == check_date and self.is_active

    @property
    def currency_pair(self) -> str:
        """Return formatted currency pair"""
        return f"{self.from_currency.code}/{self.to_currency.code}"


class ExchangeRateCreate(ExchangeRateBase):
    pass


class ExchangeRateUpdate(ExchangeRateBase):
    pass


class ExchangeRatePublic(ExchangeRateBase):
    id: UUID


class ExchangeRatesPublic(SQLModel):
    data: List[ExchangeRatePublic]
    count: int
