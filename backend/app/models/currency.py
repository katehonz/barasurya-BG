from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Index

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.exchange_rate import ExchangeRate


class CurrencyBase(BaseModel):
    code: str = Field(
        ..., max_length=3, description="ISO 4217 currency code (BGN, EUR, USD)"
    )
    name: str = Field(..., max_length=100, description="English currency name")
    name_bg: str | None = Field(
        default=None, max_length=100, description="Bulgarian currency name"
    )
    symbol: str | None = Field(
        default=None, max_length=10, description="Currency symbol (лв., €, $)"
    )
    decimal_places: int = Field(
        default=2, description="Number of decimal places for amounts"
    )
    is_active: bool = Field(default=True, description="Whether this currency is active")
    is_base_currency: bool = Field(
        default=False, description="Whether this is the base currency"
    )
    bnb_code: str | None = Field(
        default=None, max_length=3, description="Bulgarian National Bank code"
    )
    ecb_code: str | None = Field(
        default=None, max_length=3, description="European Central Bank code"
    )
    description: str | None = Field(
        default=None, description="Additional currency description"
    )


class Currency(CurrencyBase, table=True):
    __tablename__ = "currencies"

    id: UUID | None = Field(default_factory=uuid4, primary_key=True)

    # Database indexes for performance
    __table_args__ = (
        Index("ix_currency_code", "code"),
        Index("ix_currency_is_active", "is_active"),
        Index("ix_currency_is_base_currency", "is_base_currency"),
    )

    # Relationships
    exchange_rates_from: List["ExchangeRate"] = Relationship(
        back_populates="from_currency",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRate.from_currency_id]"},
    )
    exchange_rates_to: List["ExchangeRate"] = Relationship(
        back_populates="to_currency",
        sa_relationship_kwargs={"foreign_keys": "[ExchangeRate.to_currency_id]"},
    )

    @property
    def display_name(self) -> str:
        """Return localized name if available, otherwise English name"""
        return self.name_bg or self.name

    @property
    def formatted_code(self) -> str:
        """Return formatted currency code with symbol"""
        if self.symbol:
            return f"{self.code} ({self.symbol})"
        return self.code


class CurrencyCreate(CurrencyBase):
    pass


class CurrencyUpdate(CurrencyBase):
    pass


class CurrencyPublic(CurrencyBase):
    id: UUID


class CurrenciesPublic(SQLModel):
    data: List[CurrencyPublic]
    count: int
