
from typing import Optional

from sqlmodel import Field, SQLModel


class SaftCountryBase(SQLModel):
    code: str = Field(max_length=2, index=True, unique=True, sa_column_kwargs={"unique": True})
    code3: Optional[str] = Field(default=None, max_length=3, index=True, unique=True, sa_column_kwargs={"unique": True})
    numeric_code: Optional[str] = Field(default=None, max_length=3)
    name_bg: str
    name_en: str
    name_official: Optional[str] = Field(default=None)


class SaftCountry(SaftCountryBase, table=True):
    __tablename__ = 'saft_countries'
    id: Optional[int] = Field(default=None, primary_key=True)


class SaftCountryCreate(SaftCountryBase):
    pass


class SaftCountryRead(SaftCountryBase):
    id: int

